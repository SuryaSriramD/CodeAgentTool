"""Read-only bounded source access and deterministic, unapplied change proposals."""

import difflib
import hashlib
import os
import re
import threading
from collections import OrderedDict
from pathlib import Path, PurePosixPath

from integration.models import AuthorOutput, ContextAction, EvidenceReference, SuggestedEdit


class ContextError(ValueError):
    pass


SKIP_DIRS = {".git", ".hg", ".svn", "node_modules", ".venv", "venv", "env",
             "__pycache__", ".next", "dist", "build", "vendor", "target", ".idea"}
SECRET_NAMES = {".env", ".netrc", ".npmrc", ".pypirc", "credentials", "id_rsa", "id_ed25519"}
SECRET_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".keystore"}


def source_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# A snapshot's bounded lexical index is shared across finding groups and retries.
# File metadata is part of the key, so changed non-snapshot test workspaces cannot
# reuse stale locations. Content hashes in report findings still fence actual edits.
_INDEX_CACHE = OrderedDict()
_INDEX_LOCK = threading.Lock()


class SourceContext:
    def __init__(self, workspace_path: str, max_chars: int = 60000):
        self.root = Path(workspace_path).resolve(strict=True)
        if not self.root.is_dir():
            raise ContextError("Source workspace is not a directory")
        self.max_chars = max_chars
        self.used_chars = 0
        self.sources: dict[str, str] = {}
        self.delivered: dict[str, list[tuple[int, int]]] = {}
        self.paths: list[str] = []
        self.index_truncated = False
        for root, dirs, files in os.walk(self.root, followlinks=False):
            dirs[:] = sorted(d for d in dirs if d.casefold() not in SKIP_DIRS
                             and not Path(root, d).is_symlink())
            for name in sorted(files):
                rel = Path(root, name).relative_to(self.root).as_posix()
                try:
                    path = self.safe_path(rel)
                    if path.stat().st_size <= 512000:
                        self.paths.append(rel)
                except (ContextError, OSError):
                    continue
                if len(self.paths) >= 10000:
                    self.index_truncated = True
                    break
            if self.index_truncated:
                break

    def identifier_index(self) -> dict:
        signature = tuple((name, self.safe_path(name).stat().st_size,
                           self.safe_path(name).stat().st_mtime_ns) for name in self.paths)
        key = (str(self.root), signature)
        with _INDEX_LOCK:
            if key in _INDEX_CACHE:
                _INDEX_CACHE.move_to_end(key)
                return _INDEX_CACHE[key]
        identifiers, consumed, occurrences = {}, 0, 0
        for name in self.paths:
            try:
                consumed += self.safe_path(name).stat().st_size
                if consumed > 20_000_000:
                    break
                text = self.content(name)
            except (OSError, ContextError):
                continue
            for number, line in enumerate(text.splitlines(), 1):
                for word in set(re.findall(r"\b[A-Za-z_][A-Za-z_0-9]{2,79}\b", line)):
                    positions = identifiers.setdefault(word, [])
                    if len(positions) < 8:
                        positions.append((name, number))
                        occurrences += 1
                if occurrences >= 200_000:
                    break
            if occurrences >= 200_000:
                break
        result = {"identifiers": identifiers, "kind": "bounded_lexical_candidates",
                  "truncated": consumed > 20_000_000 or occurrences >= 200_000 or self.index_truncated}
        with _INDEX_LOCK:
            _INDEX_CACHE[key] = result
            while len(_INDEX_CACHE) > 8:
                _INDEX_CACHE.popitem(last=False)
        return result

    def relevant_context(self, finding: dict) -> list[dict]:
        """Prefer scanner traces; identifier matches are explicitly non-semantic."""
        results, seen = [], set()
        traces = finding.get("evidence_traces") or finding.get("evidence") or []
        locations = []
        def trace_locations(value, depth=0):
            if depth > 8 or len(locations) >= 24:
                return
            if isinstance(value, dict):
                filename = value.get("file") or value.get("path")
                start = value.get("start") or {}
                line = value.get("line") or value.get("line_start") or (start.get("line") if isinstance(start, dict) else None)
                if isinstance(filename, str) and isinstance(line, int):
                    locations.append({"file": filename, "line": line})
                for child in value.values():
                    trace_locations(child, depth + 1)
            elif isinstance(value, (list, tuple)):
                for child in value[:24]:
                    trace_locations(child, depth + 1)
        trace_locations(traces)
        for trace in locations:
            if not isinstance(trace, dict):
                continue
            filename = trace.get("file") or trace.get("path")
            line = trace.get("line") or trace.get("line_start")
            if filename and isinstance(line, int):
                try:
                    results.append({"kind": "scanner_evidence", **self.read(filename, max(1, line - 3), line + 3)})
                    seen.add((filename, line))
                except (ContextError, OSError):
                    pass
            if len(results) >= 4:
                return results
        text = self.content(finding["file"])
        line = max(1, int(finding.get("line") or 1))
        excerpt = "\n".join(text.splitlines()[max(0, line - 3):line + 2])
        words = list(dict.fromkeys(re.findall(r"\b[A-Za-z_][A-Za-z_0-9]{2,79}\b", excerpt)))
        index = self.identifier_index()
        for word in words[:12]:
            for filename, number in index["identifiers"].get(word, []):
                if (filename, number) in seen or (filename == finding["file"] and abs(number - line) < 30):
                    continue
                seen.add((filename, number))
                try:
                    results.append({"kind": "lexical_candidate", "identifier": word,
                                    **self.read(filename, max(1, number - 2), number + 3)})
                except (ContextError, OSError):
                    continue
                if len(results) >= 4:
                    return results
        return results

    def safe_path(self, relative: str) -> Path:
        if not isinstance(relative, str) or "\\" in relative or "\x00" in relative:
            raise ContextError("Invalid source path")
        parts = PurePosixPath(relative)
        if parts.is_absolute() or not parts.parts or any(p in {"..", "."} for p in parts.parts):
            raise ContextError("Source path must stay within the workspace")
        if any(p.casefold() in SKIP_DIRS for p in parts.parts):
            raise ContextError("Generated or dependency directories are excluded")
        name = parts.name.casefold()
        if name.startswith("._") or name in SECRET_NAMES or name.startswith(".env.") or Path(name).suffix in SECRET_SUFFIXES:
            raise ContextError("Credential files are excluded from AI context")
        candidate = self.root
        for part in parts.parts:
            candidate = candidate / part
            if candidate.is_symlink():
                raise ContextError("Symlinks are excluded from AI context")
        try:
            candidate.resolve(strict=True).relative_to(self.root)
        except (ValueError, OSError) as exc:
            raise ContextError("Source path is unavailable or outside the workspace") from exc
        if not candidate.is_file():
            raise ContextError("Source path is not a regular file")
        return candidate

    def content(self, relative: str, expected_hash: str | None = None) -> str:
        path = self.safe_path(relative)
        if relative not in self.sources:
            if path.stat().st_size > 512000:
                raise ContextError("Source file exceeds the bounded context file size")
            raw = path.read_bytes()
            if b"\x00" in raw:
                raise ContextError("Binary files cannot be included in AI context")
            try:
                self.sources[relative] = raw.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise ContextError("Source file is not UTF-8 text") from exc
        text = self.sources[relative]
        if expected_hash and source_hash(text) != expected_hash.removeprefix("sha256:"):
            raise ContextError("Source changed since the scan; run a new scan")
        return text

    def read(self, relative: str, line_start: int = 1, line_end: int = 100) -> dict:
        text = self.content(relative)
        lines = text.splitlines(keepends=True)
        if not lines or line_start > len(lines):
            raise ContextError("Requested source lines are unavailable")
        start = max(1, line_start)
        end = min(len(lines), line_end, start + 199)
        selected = []
        for index in range(start - 1, end):
            line = lines[index]
            if self.used_chars + sum(map(len, selected)) + len(line) > self.max_chars:
                break
            selected.append(line)
        if not selected:
            raise ContextError("Source context character budget exhausted")
        actual_end = start + len(selected) - 1
        excerpt = "".join(selected)
        self.used_chars += len(excerpt)
        self.delivered.setdefault(relative, []).append((start, actual_end))
        return {"file": relative, "source_hash": source_hash(text), "line_start": start,
                "line_end": actual_end, "content": excerpt,
                "truncated": actual_end < line_end and actual_end < len(lines)}

    def search(self, query: str) -> list[dict]:
        if not query or len(query) > 120:
            raise ContextError("Search requires a literal query of 1–120 characters")
        matches = []
        scanned_bytes = 0
        for relative in self.paths:
            try:
                size = self.safe_path(relative).stat().st_size
                scanned_bytes += size
                if scanned_bytes > 20000000:
                    break
                text = self.content(relative)
            except (ContextError, OSError):
                continue
            for index, line in enumerate(text.splitlines(), 1):
                if query in line:
                    matches.append(self.read(relative, max(1, index - 3), index + 3))
                    if len(matches) >= 8:
                        return matches
        return matches

    def act(self, action: ContextAction) -> dict:
        try:
            result = (self.read(action.file, action.line_start, action.line_end)
                      if action.kind == "read" else self.search(action.query))
            return {"request": action.model_dump(), "result": result,
                    "search_is_bounded": action.kind == "search"}
        except (ContextError, OSError) as exc:
            return {"request": action.model_dump(), "error": str(exc)}

    def evidence(self, ref: EvidenceReference) -> dict:
        if not any(start <= ref.line_start <= ref.line_end <= end
                   for start, end in self.delivered.get(ref.file, [])):
            raise ContextError("Evidence cites source lines not delivered to the agent")
        text = self.content(ref.file)
        excerpt = "".join(text.splitlines(keepends=True)[ref.line_start - 1:ref.line_end])
        return {**ref.model_dump(), "source_hash": source_hash(text), "excerpt": excerpt}

    def ensure_unchanged(self, relative: str):
        actual = self.safe_path(relative).read_bytes()
        if hashlib.sha256(actual).hexdigest() != source_hash(self.sources[relative]):
            raise ContextError("Source snapshot changed while review was running")

    def proposal(self, authored: AuthorOutput, finding_id: str) -> dict:
        edits, by_file = [], {}
        for edit in authored.edits:
            if edit.file not in self.delivered:
                raise ContextError("Proposed edit targets a file not delivered in context")
            text = self.content(edit.file)
            self.ensure_unchanged(edit.file)
            if text.count(edit.original) != 1:
                raise ContextError("Proposed original text must match source exactly once")
            if edit.original == edit.replacement:
                raise ContextError("Proposed edit does not change the source")
            start = text.index(edit.original)
            end = start + len(edit.original)
            first_line = text.count("\n", 0, start) + 1
            last_line = text.count("\n", 0, max(start, end - 1)) + 1
            if not any(a <= first_line <= last_line <= b for a, b in self.delivered[edit.file]):
                raise ContextError("Proposed edit extends beyond source delivered to the agent")
            for other_start, other_end, _ in by_file.get(edit.file, []):
                if start < other_end and other_start < end:
                    raise ContextError("Proposed edits overlap")
            by_file.setdefault(edit.file, []).append((start, end, edit.replacement))
            edits.append({**edit.model_dump(), "source_hash": source_hash(text),
                          "start_offset": start, "end_offset": end})
        differences = []
        for filename, changes in sorted(by_file.items()):
            original = self.sources[filename]
            proposed = original
            for start, end, replacement in sorted(changes, reverse=True):
                proposed = proposed[:start] + replacement + proposed[end:]
            for line in difflib.unified_diff(original.splitlines(keepends=True),
                                            proposed.splitlines(keepends=True),
                                            fromfile=f"a/{filename}", tofile=f"b/{filename}"):
                differences.append(line if line.endswith("\n") else line + "\n\\ No newline at end of file\n")
        diff = "".join(differences)
        return {"id": "proposal_" + source_hash(finding_id + diff)[:20],
                "finding_ids": [finding_id], "edits": edits, "diff": diff,
                "explanation": authored.explanation, "checks": authored.checks,
                "status": "proposed", "review": None, "applied": False, "tested": False}


def proposal_conflicts(proposals: list[dict]) -> list[dict]:
    """Flag potentially overlapping original spans, without applying source edits."""
    conflicts = []
    for index, left in enumerate(proposals):
        for right in proposals[index + 1:]:
            files = set()
            for a in left.get("edits", []):
                for b in right.get("edits", []):
                    if a["file"] != b["file"]:
                        continue
                    # Exact positions are persisted by new proposals. Legacy edits
                    # without positions are conservatively incompatible per file.
                    if a.get("source_hash") != b.get("source_hash") or "start_offset" not in a or "start_offset" not in b:
                        files.add(a["file"])
                    elif a["start_offset"] < b["end_offset"] and b["start_offset"] < a["end_offset"]:
                        files.add(a["file"])
            if files:
                conflicts.append({"proposal_ids": [left["id"], right["id"]], "files": sorted(files)})
    return conflicts


def combined_diff(context: SourceContext, proposals: list[dict], selected_ids: list[str]) -> str:
    """Explicit selection only; only statically validated reviewed edits qualify."""
    if not selected_ids or len(selected_ids) != len(set(selected_ids)):
        raise ContextError("Select distinct proposal IDs")
    selected = [p for p in proposals if p["id"] in selected_ids]
    if len(selected) != len(selected_ids):
        raise ContextError("Unknown selected proposal")
    if any(p.get("status") != "reviewed" or p.get("validation", {}).get("status") != "passed" for p in selected):
        raise ContextError("Combined diff requires reviewed, statically validated proposals")
    if proposal_conflicts(selected):
        raise ContextError("Selected proposals contain conflicting edits")
    edits = []
    for proposal in selected:
        for edit in proposal["edits"]:
            text = context.content(edit["file"], edit["source_hash"])
            context.delivered[edit["file"]] = [(1, max(1, len(text.splitlines())))]
            edits.append({key: edit[key] for key in ("file", "original", "replacement")})
    if len(edits) > 100:
        raise ContextError("Combined diff is limited to 100 anchored edits")
    # Each authored proposal remains limited to 12 edits; an explicit selection
    # may combine several already-reviewed proposals within the scanner's limit.
    authored = AuthorOutput.model_construct(edits=[SuggestedEdit.model_validate(edit) for edit in edits],
                 explanation="Explicitly selected compatible proposals", checks=[], context_requests=[])
    return context.proposal(authored, ",".join(sorted(selected_ids)))["diff"]
