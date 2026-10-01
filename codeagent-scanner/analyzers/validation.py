"""Deterministic proposed-edit checks; never execute or build repository code."""
from __future__ import annotations
from collections import Counter
import hashlib
import json
import re
from pathlib import Path, PurePosixPath
import tempfile
import threading
import time
from .base import AnalysisCancelled
from .common import DOTNET_LANGUAGES, LANGUAGE_EXTENSIONS, inventory, language_for
from .depcheck_runner import dependency_inventory
from .profiles import validate_profile
from .service import scan_workspace

_workspace_slot = threading.Semaphore(1)
MAX_FILES = 10000
MAX_BYTES = 500 * 1024 * 1024


def _flatten(report):
    return [dict(issue, file=entry['path']) for entry in report.get('files',[]) for issue in entry.get('issues',[])]


def _key(issue, root, cache):
    # Preserve literals and changed source evidence while ignoring line shifts and
    # formatting. Counts alone could hide replacement of one flaw by another.
    relative=issue.get('file')
    if relative not in cache:
        cache[relative]=_safe_path(Path(root),relative).read_bytes().decode('utf-8',errors='replace').splitlines()
    lines=cache[relative]
    start=max(1,int(issue.get('line') or 1));end=max(start,int(issue.get('end_line') or start))
    text='\n'.join(lines[start-1:end])
    tokens=re.split(r"(\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`)",text)
    evidence=''.join(part if index%2 else ''.join(part.split()) for index,part in enumerate(tokens))
    return issue.get('tool'),issue.get('rule_id'),relative,issue.get('message'),evidence


def _safe_path(root, relative):
    if not isinstance(relative,str) or '\\' in relative or '\x00' in relative:
        raise ValueError('Invalid edit path')
    path=PurePosixPath(relative)
    if path.is_absolute() or not path.parts or any(p in ('..','.') for p in path.parts):
        raise ValueError('Edit path escapes source snapshot')
    target=root.joinpath(*path.parts)
    if target.is_symlink() or not target.resolve().is_relative_to(root.resolve()):
        raise ValueError('Edit path escapes source snapshot')
    return target


def _apply(source, destination, edits, manifest, check):
    if not edits or len(edits)>100:
        raise ValueError('Validation requires 1 to 100 anchored edits')
    entries=manifest.get('files',{})
    if not entries or len(entries)>MAX_FILES: raise ValueError('Snapshot exceeds validation file limit or has no source')
    total=0
    for relative,digest in entries.items():
        check()
        src=_safe_path(source,relative)
        if not src.is_file(): raise ValueError('Source snapshot file is unavailable')
        raw=src.read_bytes();total+=len(raw)
        if total>MAX_BYTES:raise ValueError('Snapshot exceeds validation byte limit')
        if hashlib.sha256(raw).hexdigest()!=digest:raise ValueError('Source snapshot has changed')
        dst=_safe_path(destination,relative);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(raw)
    by_path={}
    for edit in edits:
        relative=edit.get('file') or edit.get('file_path')
        if relative not in entries:raise ValueError('Edit does not reference a snapshot file')
        if edit.get('source_hash')!=entries[relative]:raise ValueError('Edit source hash does not match snapshot')
        original,replacement=edit.get('original'),edit.get('replacement')
        if not isinstance(original,str) or not original or not isinstance(replacement,str):raise ValueError('Edit requires exact original and replacement text')
        if len(replacement.encode())>2*1024*1024:raise ValueError('Replacement exceeds validation edit limit')
        text=_safe_path(source,relative).read_bytes().decode('utf-8')
        start,end=edit.get('start_offset'),edit.get('end_offset')
        if start is not None or end is not None:
            if not isinstance(start,int) or not isinstance(end,int) or start<0 or end<=start or text[start:end]!=original:
                raise ValueError('Edit offsets do not match original source')
        else:
            if text.count(original)!=1:raise ValueError('Original edit content must match exactly once')
            start=text.index(original);end=start+len(original)
        by_path.setdefault(relative,[]).append((start,end,replacement))
    for relative,changes in by_path.items():
        check()
        ordered=sorted(changes)
        if any(left[1]>right[0] for left,right in zip(ordered,ordered[1:])):raise ValueError('Proposal contains overlapping edits')
        path=_safe_path(destination,relative);text=path.read_bytes().decode('utf-8')
        for start,end,replacement in reversed(ordered):text=text[:start]+replacement+text[end:]
        path.write_bytes(text.encode('utf-8'))
        total+=path.stat().st_size-_safe_path(source,relative).stat().st_size
        if total>MAX_BYTES:raise ValueError('Edited snapshot exceeds validation byte limit')
    return set(by_path)


def _completed_outcome(entry):
    if (not isinstance(entry,dict) or not isinstance(entry.get('path'),str)
            or entry.get('status')!='completed' or entry.get('errors')):
        return False
    # Older adapters lack parser details. Once present, that evidence cannot be
    # overridden by a contradictory per-file or aggregate success status.
    if 'parser' in entry:
        parser=entry['parser']
        if (not isinstance(parser,dict) or parser.get('status')!='completed'
                or not isinstance(parser.get('errors'),list) or parser['errors']):
            return False
    return True


def _coverage_errors(report, root, selected, changed, targets):
    """Check fresh scanner evidence, independent of its aggregate status.

    In particular, an empty/duplicate per-file report must not validate a fix.
    Required edited/target paths are added to the inventory so an exclusion
    cannot silently make a proposed source change appear checked.
    """
    languages={'semgrep':set(LANGUAGE_EXTENSIONS)-DOTNET_LANGUAGES,
               'bandit':{'python'},'dotnet':DOTNET_LANGUAGES}
    expected={name:{path for path,_ in inventory(root,languages[name])}
              if name in languages else {path for path,_ in dependency_inventory(root)[0]}
              for name in selected}
    for name in selected:
        if name in languages:
            expected[name].update(path for path in changed if language_for(Path(path)) in languages[name])
        expected[name].update(t.get('file') or t.get('file_path') for t in targets
                              if t.get('tool')==name and isinstance(t.get('file') or t.get('file_path'),str))
    problems=[]
    entries=report.get('coverage')
    if not isinstance(entries,list):
        return [(name,'missing or invalid coverage report') for name in selected]
    for name in selected:
        candidates=[entry for entry in entries if isinstance(entry,dict) and entry.get('tool')==name]
        if len(candidates)!=1:
            problems.append((name,'expected one scanner coverage entry'))
            continue
        coverage=candidates[0];paths=expected[name]
        if coverage.get('status')!=('completed' if paths else 'skipped'):
            problems.append((name,'incomplete scanner coverage'))
        if coverage.get('errors'):
            problems.append((name,'scanner reported coverage errors'))
        outcomes=coverage.get('path_outcomes')
        if not isinstance(outcomes,list):
            problems.append((name,'missing per-file coverage evidence'))
            continue
        counts=Counter(entry.get('path') for entry in outcomes
                       if isinstance(entry,dict) and isinstance(entry.get('path'),str))
        completed={entry['path'] for entry in outcomes if _completed_outcome(entry)}
        missing=paths-completed
        if missing:
            problems.append((name,f'{len(missing)} required files were not fully checked: '+', '.join(sorted(missing)[:10])))
        if (len(outcomes)!=len(paths) or set(counts)!=paths or any(count!=1 for count in counts.values())):
            problems.append((name,'per-file coverage inventory is missing, duplicated, or unexpected'))
        for field,value in (('files_discovered',len(paths)),('files_scanned',len(paths)),('files_skipped',0)):
            if type(coverage.get(field)) is not int or coverage[field]!=value:
                problems.append((name,'coverage file counts do not match the required inventory'))
                break
        scanned=coverage.get('scanned_paths')
        if not isinstance(scanned,list) or any(not isinstance(path,str) for path in scanned) or set(scanned)!=paths or len(scanned)!=len(paths):
            problems.append((name,'scanned paths do not match the required inventory'))
    if any(not isinstance(entry,dict) or entry.get('tool') not in selected for entry in entries):
        problems.append(('scanner','unexpected scanner coverage entry'))
    return problems


def validate_proposal(snapshot_root, body, cancel=lambda:False):
    """Validate body against snapshot_root/{manifest.json,source/}; return retained evidence."""
    start=time.monotonic();deadline=start+min(120,max(.01,float(body.get('timeout_sec',120))))
    result={'status':'incomplete','syntax':{'status':'incomplete','errors':[]},
            'target_findings_remaining':[],'introduced_findings':[],'coverage_before':[],'coverage_after':[],
            'profile_digests':{},'tool_runs':[],'errors':[],'elapsed_ms':0,'applied':False,'runtime_tested':False}
    held=False
    def check():
        if cancel():raise AnalysisCancelled('Proposal validation canceled')
        if time.monotonic()>=deadline:raise TimeoutError('Proposal validation exceeded its time budget')
    try:
        profile=validate_profile(body.get('profile','security-v1'))
        while not held:
            check();held=_workspace_slot.acquire(timeout=min(.1,max(.001,deadline-time.monotonic())))
        snapshot=Path(snapshot_root).resolve(strict=True);source=snapshot/'source'
        manifest=json.loads((snapshot/'manifest.json').read_text())
        # Verify the entire inventory, including unexpected files and symlinks.
        from ingestion.snapshots import verify_snapshot
        verify_snapshot(source,manifest);check()
        with tempfile.TemporaryDirectory(prefix='codeagent-validation-') as scratch:
            changed=_apply(source,Path(scratch),body.get('edits',[]),manifest,check)
            targets=body.get('target_findings',[])
            if not targets:raise ValueError('Validation requires original target finding evidence')
            selected=[]
            languages={language_for(Path(path)) for path in changed}
            if languages-DOTNET_LANGUAGES-{None}:selected.append('semgrep')
            if languages & DOTNET_LANGUAGES:selected.append('dotnet')
            if 'python' in languages:selected.append('bandit')
            dependency_paths={p for p,_ in dependency_inventory(source)[0]}
            if changed & dependency_paths:selected.append('depcheck')
            selected.extend(t['tool'] for t in targets if t.get('tool') in ('semgrep','dotnet','bandit','depcheck'))
            selected=list(dict.fromkeys(selected))
            if not selected:raise ValueError('No trusted parser/scanner supports these proposed edits')
            before=scan_workspace(source,selected,timeout_sec=max(.01,deadline-time.monotonic()),cancel=cancel,profile=profile)
            result['coverage_before']=before['coverage'];result['profile_digests']=before.get('profile_digests',{})
            result['tool_runs'].extend(dict(run,phase='before') for run in before['tool_runs']);check()
            coverage_before_errors=_coverage_errors(before,source,selected,changed,targets)
            baseline=_flatten(before)
            missing=[]
            for target in targets:
                path=target.get('file') or target.get('file_path')
                matches=[i for i in baseline if i.get('rule_id')==target.get('rule_id') and i.get('tool')==target.get('tool') and i['file']==path and i.get('line')==target.get('line')]
                if not matches:missing.append(target.get('id','unknown'))
            after=scan_workspace(scratch,selected,timeout_sec=max(.01,deadline-time.monotonic()),cancel=cancel,profile=profile)
            result['coverage_after']=after['coverage'];result['tool_runs'].extend(dict(run,phase='after') for run in after['tool_runs']);check()
            coverage_after_errors=_coverage_errors(after,Path(scratch),selected,changed,targets)
            findings=_flatten(after)
            # Conservatively retain a target if another finding of its rule remains
            # in that file. This avoids claiming a fix when line numbers shift.
            result['target_findings_remaining']=[t['id'] for t in targets if any(i.get('tool')==t.get('tool') and i.get('rule_id')==t.get('rule_id') and i['file']==(t.get('file') or t.get('file_path')) for i in findings)]
            before_evidence,after_evidence={},{}
            remaining=Counter(_key(i,source,before_evidence) for i in baseline)
            for finding in findings:
                key=_key(finding,Path(scratch),after_evidence)
                if remaining[key]>0:remaining[key]-=1
                else:result['introduced_findings'].append(finding)
            parse_errors=[f'{tool}: {error}' for tool,error in coverage_after_errors if tool!='depcheck']
            result['syntax']={'status':'incomplete' if parse_errors else 'passed','errors':parse_errors}
            incomplete=(before['status']!='completed' or after['status']!='completed' or bool(missing)
                        or bool(coverage_before_errors) or bool(coverage_after_errors))
            if missing:result['errors'].append('Target findings were not reproduced in the baseline: '+', '.join(missing))
            if before.get('profile_digests')!=after.get('profile_digests'):incomplete=True;result['errors'].append('Scanner profiles changed during validation')
            for phase,problems in (('before',coverage_before_errors),('after',coverage_after_errors)):
                result['errors'].extend(f'{phase} {tool}: {error}' for tool,error in problems)
            check()
            result['status']='incomplete' if incomplete else 'failed' if result['target_findings_remaining'] or result['introduced_findings'] else 'passed'
    except AnalysisCancelled:raise
    except (ValueError,UnicodeError) as exc:
        result['status']='failed';result['errors'].append(str(exc))
    except Exception as exc:
        result['status']='incomplete';result['errors'].append(str(exc))
    finally:
        if held:_workspace_slot.release()
        result['elapsed_ms']=round((time.monotonic()-start)*1000)
    return result
