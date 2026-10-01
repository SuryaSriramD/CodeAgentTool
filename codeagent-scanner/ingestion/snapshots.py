"""Bounded GitHub archive/ZIP ingestion, independent of scanned build systems."""
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse, quote
import fnmatch
import hashlib
import json
import re
import shutil
import stat
import zipfile

import httpx

from .policy import SOURCE_POLICY_VERSION, excluded_source_path


class SourceError(ValueError):
    pass


class SourceCanceled(Exception):
    pass


def validate_github_url(value):
    url = urlparse(value)
    parts = url.path.strip("/").removesuffix(".git").split("/")
    if (url.scheme != "https" or url.netloc != "github.com" or url.username or url.query or url.fragment
            or len(parts) != 2 or any(not re.fullmatch(r"[A-Za-z0-9_.-]+", part) or part in {".", ".."} for part in parts)):
        raise SourceError("Use an HTTPS github.com owner/repository URL without credentials or query parameters")
    return parts[0], parts[1]


def checked_cancel(cancel):
    if cancel():
        raise SourceCanceled("Canceled")


def github_repository_identity(url, settings):
    """Resolve project/default-branch identity before a submission pins its baseline."""
    owner, repo = validate_github_url(url)
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "CodeAgent-Scanner"}
    if settings.github_token:
        headers["Authorization"] = "Bearer " + settings.github_token
    try:
        with httpx.Client(timeout=15, follow_redirects=False, trust_env=False) as client:
            response = client.get(f"https://api.github.com/repos/{owner}/{repo}", headers=headers)
            if response.status_code == 301:
                location = response.headers.get('location', '')
                target = urlparse(location)
                if target.scheme != 'https' or target.netloc != 'api.github.com' or target.username:
                    raise SourceError('GitHub repository identity redirected outside the API host')
                response = client.get(location, headers=headers)
            if response.status_code in (401, 403, 404):
                raise SourceError('Repository unavailable or access denied; check the URL and server-side GitHub token')
            response.raise_for_status()
            value = response.json()
            if not isinstance(value.get('id'), int) or not isinstance(value.get('default_branch'), str):
                raise SourceError('GitHub returned incomplete repository identity')
            canonical = value.get('html_url') or url
            validate_github_url(canonical)
            return {'id': value['id'], 'default_branch': value['default_branch'], 'url': canonical}
    except (httpx.HTTPError, ValueError, TypeError) as exc:
        if isinstance(exc, SourceError):
            raise
        raise SourceError('GitHub repository identity could not be resolved; check connectivity and retry') from exc


def fetch_github_archive(source, output: Path, settings, cancel=lambda: False, client=None):
    owner, repo = validate_github_url(source["url"])
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "CodeAgent-Scanner"}
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"
    own_client = client is None
    client = client or httpx.Client(timeout=httpx.Timeout(30, read=15), follow_redirects=False, trust_env=False)

    def get_json(path):
        checked_cancel(cancel)
        try:
            response = client.get("https://api.github.com" + path, headers=headers)
        except httpx.HTTPError as exc:
            raise SourceError("GitHub could not be reached; check connectivity and retry") from exc
        if response.status_code in (401, 403, 404):
            raise SourceError("Repository/ref unavailable or access denied; check the URL and server-side GitHub token")
        if response.status_code != 200:
            raise SourceError(f"GitHub request failed (HTTP {response.status_code})")
        return response.json()

    try:
        base = f"/repos/{owner}/{repo}"
        ref = source.get("commit") or source.get("ref")
        repository = get_json(base) if (source.get("project_id") and not source.get('repository_id')) or not ref else {}
        if not ref:
            ref = repository["default_branch"]
        sha = get_json(base + "/commits/" + quote(ref, safe=""))["sha"]
        if not re.fullmatch(r"[0-9a-fA-F]{40,64}", sha):
            raise SourceError("GitHub returned an invalid source identity")
        checked_cancel(cancel)
        response = client.get("https://api.github.com" + base + "/zipball/" + sha, headers=headers)
        if response.status_code != 302:
            raise SourceError(f"GitHub archive unavailable (HTTP {response.status_code})")
        location = response.headers.get("location", "")
        parsed = urlparse(location)
        if parsed.scheme != "https" or parsed.netloc != "codeload.github.com" or parsed.username:
            raise SourceError("GitHub archive redirect is outside the allowed download host")
        # No API credential is forwarded to the archive host or retained on disk.
        with client.stream("GET", location, headers={"User-Agent": "CodeAgent-Scanner"}) as download:
            if download.status_code != 200:
                raise SourceError(f"Archive download failed (HTTP {download.status_code})")
            size = 0
            with output.open("wb") as handle:
                for block in download.iter_bytes(65536):
                    checked_cancel(cancel)
                    size += len(block)
                    if size > settings.max_upload_size:
                        raise SourceError("Repository archive exceeds MAX_UPLOAD_SIZE")
                    handle.write(block)
        return {**source, "ref": source.get("ref") or ref, "commit": sha,
                **({"repository_id": repository["id"]} if isinstance(repository.get("id"), int) else {})}
    except httpx.HTTPError as exc:
        raise SourceError("Archive download interrupted; retry the job") from exc
    finally:
        if own_client:
            client.close()


def extract_zip(archive: Path, destination: Path, settings, cancel=lambda: False):
    destination.mkdir(parents=True, exist_ok=False)
    try:
        with zipfile.ZipFile(archive) as zipped:
            members = zipped.infolist()
            if len(members) > settings.max_files:
                raise SourceError("Archive exceeds MAX_FILES_PER_JOB")
            expanded = 0
            seen = set()
            for item in members:
                checked_cancel(cancel)
                path = PurePosixPath(item.filename)
                if (not item.filename or "\\" in item.filename or "\x00" in item.filename or path.is_absolute()
                        or any(p in {"..", "."} or ":" in p for p in path.parts)):
                    raise SourceError("Archive contains an unsafe path")
                mode = item.external_attr >> 16
                if stat.S_ISLNK(mode) or (stat.S_IFMT(mode) and not (stat.S_ISREG(mode) or stat.S_ISDIR(mode))):
                    raise SourceError("Archive contains a symlink or special file")
                normalized = str(path).casefold()
                if normalized in seen:
                    raise SourceError("Archive contains duplicate or case-colliding paths")
                seen.add(normalized)
                expanded += item.file_size
                if expanded > settings.max_expanded_size:
                    raise SourceError("Archive exceeds MAX_EXPANDED_SIZE")
                if item.flag_bits & 1:
                    raise SourceError("Encrypted ZIP files are unsupported")
            actual = 0
            for item in members:
                checked_cancel(cancel)
                target = destination.joinpath(*PurePosixPath(item.filename).parts)
                if not target.resolve().is_relative_to(destination.resolve()):
                    raise SourceError("Archive path escapes the workspace")
                if item.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with zipped.open(item) as src, target.open("xb") as dst:
                    while block := src.read(65536):
                        checked_cancel(cancel)
                        actual += len(block)
                        if actual > settings.max_expanded_size:
                            raise SourceError("Expanded archive exceeds configured limit")
                        dst.write(block)
    except (zipfile.BadZipFile, OSError, RuntimeError) as exc:
        shutil.rmtree(destination, ignore_errors=True)
        raise SourceError("Invalid or unreadable ZIP archive") from exc
    except BaseException:
        shutil.rmtree(destination, ignore_errors=True)
        raise


def matches(path, patterns):
    return any(fnmatch.fnmatchcase(path, p) or (p.startswith("**/") and fnmatch.fnmatchcase(path, p[3:])) for p in patterns)


def build_snapshot(archive: Path, snapshot_id: str, settings, source: dict, config: dict, cancel=lambda: False):
    root = settings.storage / "snapshots" / snapshot_id
    manifest_file = root / "manifest.json"
    if manifest_file.exists():
        manifest = json.loads(manifest_file.read_text())
        verify_snapshot(root / "source", manifest)
        return manifest
    # The identifier is created by our queue. Only an incomplete staging directory is replaced.
    staging = settings.storage / "tmp" / snapshot_id
    shutil.rmtree(staging, ignore_errors=True)
    extract_zip(archive, staging, settings, cancel)
    entries = list(staging.iterdir())
    # GitHub adds a transport wrapper; ZIP paths belong to the user's source.
    # Stripping a ZIP's sole src/ directory breaks include/exclude patterns.
    content = entries[0] if source.get("source") == "github" and len(entries) == 1 and entries[0].is_dir() else staging
    files, warnings = {}, []
    source_inventory = sorted(path.relative_to(content).as_posix() for path in content.rglob("*") if path.is_file())
    ignored = 0
    for path in sorted(content.rglob("*")):
        checked_cancel(cancel)
        if not path.is_file():
            continue
        rel = path.relative_to(content).as_posix()
        excluded = (excluded_source_path(rel)
                    or (config.get("include") and not matches(rel, config["include"]))
                    or matches(rel, config.get("exclude", [])))
        if excluded:
            path.unlink()
            ignored += 1
            continue
        raw = path.read_bytes()
        # Retain the presence of unsupported binary Bun locks for an explicit
        # dependency-coverage error; AI context still rejects binary contents.
        utf16 = raw.startswith((b"\xff\xfe", b"\xfe\xff"))
        if len(raw) > 20 * 1024 * 1024 or (b"\x00" in raw and path.name != "bun.lockb" and not utf16):
            path.unlink()
            ignored += 1
            continue
        if utf16:
            warnings.append(f"UTF-16 source retained for scanner coverage; AI source context requires UTF-8: {rel}")
        if raw.startswith(b"version https://git-lfs.github.com/spec/v1"):
            warnings.append(f"Git LFS content excluded: {rel}")
            path.unlink()
            continue
        if path.name == ".gitmodules":
            warnings.append("Git submodule contents are excluded from archive ingestion")
        files[rel] = hashlib.sha256(raw).hexdigest()
    if ignored:
        warnings.append(f"{ignored} files excluded by source, credential, binary, or size filters")
    digest = hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()
    manifest = {"id": snapshot_id, "digest": digest, "files": files, "warnings": warnings, "source": source,
                "source_inventory": source_inventory, "inventory_complete": not any("submodule" in warning for warning in warnings),
                "excluded_files": [name for name in source_inventory if name not in files],
                "ingestion_version": 3, "source_policy_version": SOURCE_POLICY_VERSION}
    root.mkdir(parents=True, exist_ok=True)
    destination = root / "source"
    if destination.exists():
        shutil.rmtree(destination)
    shutil.move(str(content), destination)
    if staging.exists():
        shutil.rmtree(staging)
    temp = root / "manifest.json.tmp"
    temp.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    temp.replace(manifest_file)
    return manifest


def verify_snapshot(path: Path, manifest):
    actual = {}
    for file in path.rglob("*"):
        if file.is_symlink():
            raise SourceError("Source snapshot contains a symlink")
        if file.is_file():
            actual[file.relative_to(path).as_posix()] = hashlib.sha256(file.read_bytes()).hexdigest()
    if actual != manifest["files"]:
        raise SourceError("Source snapshot has changed; create a new scan")
