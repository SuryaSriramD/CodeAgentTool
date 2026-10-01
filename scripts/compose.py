#!/usr/bin/env python3
"""Run the canonical Compose stack with metadata-free temporary build contexts.

Useful on macOS external drives where Docker fails while reading AppleDouble
extended attributes. The original .env, Compose project, and volumes are used.
"""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CONTEXTS = ("codeagent-scanner", "codeagent-scanner-ui")
SKIP_DIRECTORIES = {
    ".git", ".venv", "venv", "node_modules", "bin", "obj", "publish",
    "__pycache__", ".pytest_cache", ".next", ".next-test", "test-results",
    "playwright-report",
}


def stage_sources(destination: Path) -> int:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", *CONTEXTS],
        cwd=ROOT, check=True, stdout=subprocess.PIPE,
    )
    copied = 0
    prepared_directories: set[Path] = set()
    for entry in set(result.stdout.split(b"\0")):
        if not entry:
            continue
        relative = Path(entry.decode("utf-8", errors="surrogateescape"))
        if relative.is_absolute() or ".." in relative.parts or relative.parts[0] not in CONTEXTS:
            continue
        if any(part.lower() in SKIP_DIRECTORIES or part.startswith("._") for part in relative.parts):
            continue
        if (relative.parts[0] == "codeagent-scanner" and len(relative.parts) > 1
                and relative.parts[1] in {"storage", "uploads", "reports", "reviews", "tmp"}):
            continue
        if relative.name.startswith(".env") or relative.name == ".DS_Store":
            continue
        source = ROOT / relative
        if any(parent.is_symlink() for parent in (source, *source.parents) if parent != ROOT):
            continue
        if not source.is_file():  # Git also lists tracked files deleted in this checkout.
            continue
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        # COPY keeps these modes in the image; a host umask of 077 must not
        # make source unreadable to the containers' nonroot runtime users.
        for directory in target.parents:
            if directory == destination:
                break
            if directory not in prepared_directories:
                directory.chmod(0o755)
                prepared_directories.add(directory)
        shutil.copyfile(source, target)  # Deliberately exclude extended attributes.
        target.chmod(0o755 if source.stat().st_mode & 0o111 else 0o644)
        copied += 1
    for context in CONTEXTS:
        if not (destination / context / "Dockerfile").is_file():
            raise RuntimeError(f"Missing {context}/Dockerfile in the Git source inventory")
    report_page = destination / "codeagent-scanner-ui/app/reports/[reportId]/page.tsx"
    if not report_page.is_file():
        raise RuntimeError("The UI report route is missing from the staged source inventory")
    return copied


def main() -> int:
    if not sys.argv[1:] or sys.argv[1:] in (["-h"], ["--help"]):
        print("Usage: python3 scripts/compose.py <docker compose arguments>")
        print("Example: python3 scripts/compose.py up --build -d")
        print("Uses the canonical compose file, original .env, and existing named volumes.")
        return 0
    with tempfile.TemporaryDirectory(prefix="codeagent-compose-") as temporary:
        staging = Path(temporary)
        print("Preparing metadata-free Docker build contexts…", flush=True)
        count = stage_sources(staging)
        scanner = str(staging / "codeagent-scanner")
        frontend = str(staging / "codeagent-scanner-ui")
        override = staging / "build-contexts.json"
        override.write_text(json.dumps({"services": {
            name: {"build": {"context": frontend if name == "frontend" else scanner}}
            for name in ("backend", "worker", "scanner", "advisory-db", "frontend")
        }}), encoding="utf-8")
        command = ["docker", "compose", "--project-directory", str(ROOT)]
        if (ROOT / ".env").is_file():
            command.extend(["--env-file", str(ROOT / ".env")])
        command.extend(["-f", str(ROOT / "docker-compose.yml"), "-f", str(override), *sys.argv[1:]])
        print(f"Copied {count} source files; using the existing CodeAgent Compose project.", flush=True)
        return subprocess.run(command, cwd=ROOT).returncode


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"Compose wrapper failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
