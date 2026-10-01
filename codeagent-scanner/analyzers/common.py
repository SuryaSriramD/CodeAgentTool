"""One inventory and coverage vocabulary for all scanner adapters."""
from __future__ import annotations
import os
import shutil
import subprocess
import time
import threading
from email.parser import Parser
from pathlib import Path
from .base import AnalyzerResult, AnalysisCancelled, terminate_process_group
from ingestion.policy import IGNORED_DIRS, excluded_source_path

ROOT = Path(__file__).resolve().parent.parent
LANGUAGE_EXTENSIONS = {
    "python": {".py", ".pyw"}, "javascript": {".js", ".jsx", ".mjs", ".cjs"},
    "typescript": {".ts", ".tsx"}, "java": {".java"}, "go": {".go"},
    "c": {".c", ".h"}, "cpp": {".cpp", ".cc", ".cxx", ".hpp", ".hxx"},
    "ruby": {".rb"}, "php": {".php"}, "scala": {".scala"}, "kotlin": {".kt", ".kts"},
    "swift": {".swift"}, "csharp": {".cs"}, "fsharp": {".fs", ".fsx", ".fsi"},
    "vb": {".vb"}, "rust": {".rs"}, "bash": {".sh", ".bash"},
    "yaml": {".yaml", ".yml"}, "json": {".json"}, "xml": {".xml"},
    "html": {".html", ".htm"}, "dockerfile": {".dockerfile"},
}
DOTNET_LANGUAGES = {"csharp", "fsharp", "vb"}
SOURCE_LANGUAGES = set(LANGUAGE_EXTENSIONS) - {"yaml", "json", "xml", "html", "dockerfile"}

def language_for(path):
    if path.name.lower() == "dockerfile" or path.name.lower().endswith(".dockerfile"):
        return "dockerfile"
    return next((lang for lang, exts in LANGUAGE_EXTENSIONS.items() if path.suffix.lower() in exts), None)

def inventory(workspace, languages=None):
    root = Path(workspace).resolve()
    wanted = set(languages) if languages is not None else None
    files = []
    for base, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in IGNORED_DIRS and not Path(base, d).is_symlink())
        for name in sorted(names):
            path = Path(base, name)
            if excluded_source_path(path.relative_to(root).as_posix()) or path.is_symlink() or not path.is_file():
                continue
            lang = language_for(path)
            if wanted is None or lang in wanted:
                files.append((path.relative_to(root).as_posix(), lang))
    return files

def executable(name):
    configured = os.getenv(f"CODEAGENT_{name.upper().replace('-', '_')}_BIN")
    return shutil.which(configured or name)

_VERSION_CACHE = {}
_VERSION_LOCKS = {}
_VERSION_LOCKS_GUARD = threading.Lock()
VERSION_PROBE_TIMEOUT = 5


def command_version(name, binary, command, runner=None):
    """One bounded probe per executable; kill wrapper children on interruption."""
    key=(name,binary,tuple(command))
    with _VERSION_LOCKS_GUARD:
        lock=_VERSION_LOCKS.setdefault(key,threading.Lock())
    owner=getattr(runner,'__self__',None)
    while not lock.acquire(timeout=.1):
        if owner and getattr(owner,'cancel',lambda:False)():raise AnalysisCancelled('Version probe canceled')
        if owner and time.monotonic()>=getattr(owner,'_command_deadline',float('inf')):
            raise subprocess.TimeoutExpired(command,getattr(owner,'timeout_sec',0))
    try:
        cached=_VERSION_CACHE.get(key)
        if cached and time.monotonic()-cached[0]<(60 if cached[1]!='unavailable' else 3):return cached[1]
        version='unavailable'
        env={**{k:v for k,v in os.environ.items() if not k.startswith(('SEMGREP_','TRIVY_'))},
             'SEMGREP_ENABLE_VERSION_CHECK':'0','SEMGREP_SEND_METRICS':'off','TRIVY_DISABLE_TELEMETRY':'true'}
        try:
            if runner:
                proc=runner(command,str(ROOT),env=env)
                output,code=proc.stdout,proc.returncode
            else:
                process=subprocess.Popen(command,cwd=str(ROOT),stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                                         text=True,encoding='utf-8',errors='replace',env=env,start_new_session=os.name=='posix')
                try:
                    output,_=process.communicate(timeout=VERSION_PROBE_TIMEOUT)
                    code=process.returncode
                except BaseException:
                    terminate_process_group(process)
                    process.communicate()
                    raise
            if code==0 and output.strip():version=output.strip().splitlines()[0]
        except (OSError,subprocess.SubprocessError):pass
        _VERSION_CACHE[key]=(time.monotonic(),version)
        return version
    finally:lock.release()


def installed_python_version(binary,name):
    """Read metadata only for a verified wheel entrypoint in that binary's venv."""
    path=Path(binary).resolve()
    try:
        header=path.read_bytes()[:512].decode('utf-8')
        first=header.splitlines()[0]
        interpreter=Path(first[2:].strip()) if first.startswith('#!') else None
        if (path.name!=name or interpreter is None or not interpreter.name.startswith('python')
                or interpreter.parent!=path.parent or not interpreter.is_file()
                or f'from {name}.' not in header):return None
        candidates=list(path.parent.parent.glob(f'lib/python*/site-packages/{name}-*.dist-info/METADATA'))
        if len(candidates)!=1:return None
        metadata=Parser().parsestr(candidates[0].read_text())
        if metadata['Name'].lower()!=name.lower():return None
        return metadata['Version']
    except (OSError,UnicodeError,IndexError,AttributeError):return None


def tool_version(name, runner=None):
    binary=executable(name)
    if not binary:return 'unavailable'
    if name=='bandit':
        installed=installed_python_version(binary,name)
        if installed:return 'bandit '+installed
    if name=='semgrep' and not os.getenv('CODEAGENT_SEMGREP_BIN'):
        # The Python wrapper starts another Python process even for --version.
        # Ask the bundled native engine directly, still requiring the selected wrapper.
        from .semgrep_runner import semgrep_core
        core=semgrep_core()
        if core:
            version=command_version(name,binary,[core,'-version'],runner)
            prefix='semgrep-core version: '
            return version[len(prefix):].split()[0] if version.startswith(prefix) else version
    return command_version(name,binary,[binary,'--version'],runner)

def result(tool, started, files, scanned=(), issues=(), errors=(), version="unknown", status=None):
    paths = [p for p, _ in files]
    completed = sorted(set(scanned).intersection(paths))
    errors = list(errors)
    if status is None:
        status = "skipped" if not paths else ("partial" if errors and completed else "failed" if errors else "completed")
    return AnalyzerResult(tool, status in {"completed", "skipped"}, list(issues),
                          int((time.monotonic() - started) * 1000), "; ".join(errors) or None, status,
                          {"tool": tool, "status": status, "files_discovered": len(paths),
                           "files_scanned": len(completed), "files_skipped": len(paths) - len(completed),
                           "errors": errors, "version": version,
                           "languages": sorted({lang for _, lang in files if lang}), "scanned_paths": completed,
                           "path_outcomes": [{"path":path,"language":lang,"status":"completed" if path in completed else "not_assessed"} for path,lang in files]})
