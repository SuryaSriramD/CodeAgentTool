"""Shared source-path policy for ingestion and every scanner inventory.

``bin`` is a conventional source location for command-line entry points as well
as a build-output location. Its name alone is not evidence of generated output.
Keep its text sources and dependency evidence; discard recognizable compiled
artifacts and the existing dedicated build/cache directories instead.
"""
from pathlib import PurePosixPath

SOURCE_POLICY_VERSION = 3
IGNORED_DIRS = frozenset({
    ".git", ".svn", "node_modules", "vendor", ".venv", "venv", "__pycache__",
    "target", "dist", "build", "obj", ".next", ".pytest_cache",
})
BINARY_SUFFIXES = frozenset({
    ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".gz", ".jar",
    ".dll", ".exe", ".so", ".woff", ".woff2", ".mp4", ".mp3", ".pyc",
    ".pyo", ".pdb", ".o", ".obj", ".a", ".lib", ".dylib", ".class",
})
SECRET_NAMES = frozenset({".env", ".netrc", ".npmrc", ".pypirc", "credentials", "id_rsa", "id_ed25519"})
SECRET_SUFFIXES = frozenset({".pem", ".key", ".p12", ".pfx", ".keystore"})


def excluded_source_path(relative_path):
    """Classify a relative file path; byte/size and user filters run separately."""
    path = PurePosixPath(relative_path)
    return (
        any(part in IGNORED_DIRS for part in path.parts[:-1])
        or path.name.startswith("._") or path.name == ".DS_Store"
        or path.name.casefold() in SECRET_NAMES or path.name.casefold().startswith(".env.")
        or path.suffix.lower() in BINARY_SUFFIXES | SECRET_SUFFIXES
    )
