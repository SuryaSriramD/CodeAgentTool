"""One configuration source for API and worker; secrets never enter job records."""
from dataclasses import dataclass, field
from pathlib import Path
import os


@dataclass
class Settings:
    storage: Path = field(default_factory=lambda: Path(os.getenv("STORAGE_BASE", "./storage")).resolve())
    max_upload_size: int = field(default_factory=lambda: int(os.getenv("MAX_UPLOAD_SIZE", "52428800")))
    max_expanded_size: int = field(default_factory=lambda: int(os.getenv("MAX_EXPANDED_SIZE", "524288000")))
    max_files: int = field(default_factory=lambda: int(os.getenv("MAX_FILES_PER_JOB", "10000")))
    max_jobs: int = field(default_factory=lambda: int(os.getenv("MAX_CONCURRENT_JOBS", "2")))
    workspace_password: str = field(default_factory=lambda: os.getenv("WORKSPACE_PASSWORD", ""), repr=False)
    session_secret: str = field(default_factory=lambda: os.getenv("SESSION_SECRET", ""), repr=False)
    team_mode: bool = field(default_factory=lambda: os.getenv("TEAM_MODE", "false").lower() == "true")
    cookie_secure: bool = field(default_factory=lambda: os.getenv("COOKIE_SECURE", "false").lower() == "true")
    github_token: str = field(default_factory=lambda: os.getenv("GITHUB_TOKEN", ""), repr=False)
    openai_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""), repr=False)
    ollama_url: str = field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
    worker_lease_sec: int = 30
    snapshot_retention_days: int = field(default_factory=lambda: int(os.getenv("JOB_RETENTION_DAYS", "7")))
    report_retention_days: int = field(default_factory=lambda: int(os.getenv("REPORT_RETENTION_DAYS", "30")))

    def prepare(self):
        if self.team_mode and (not self.workspace_password or len(self.session_secret) < 32):
            raise ValueError("TEAM_MODE requires WORKSPACE_PASSWORD and SESSION_SECRET (at least 32 characters)")
        if not 1 <= self.max_jobs <= 16:
            raise ValueError("MAX_CONCURRENT_JOBS must be between 1 and 16")
        for name in ("uploads", "snapshots", "reports", "reviews", "tmp"):
            (self.storage / name).mkdir(parents=True, exist_ok=True)

    def redact(self, message: str) -> str:
        for secret in (self.github_token, self.openai_key, self.workspace_password, self.session_secret):
            if secret:
                message = message.replace(secret, "[redacted]")
        return message[:2000]
