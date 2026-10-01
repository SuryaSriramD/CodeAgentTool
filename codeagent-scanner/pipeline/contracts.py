"""Versioned public contracts shared by OpenAPI and the generated UI types."""
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field

Status = Literal["queued", "running", "completed", "partial", "failed", "canceled", "interrupted"]


class ReviewConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    provider: Literal["openai", "ollama"] = "ollama"
    model: str = Field(default="", max_length=200)
    workflow_mode: Literal["multi_agent", "single_agent"] = "multi_agent"
    min_severity: Literal["critical", "high", "medium", "low"] = "high"
    max_model_calls: int = Field(default=60, ge=1, le=200)
    max_total_tokens: int = Field(default=100000, ge=1000, le=1000000)
    timeout_sec: int = Field(default=900, ge=60, le=7200)
    max_findings: int = Field(default=20, ge=1, le=100)
    max_context_chars: int = Field(default=60000, ge=1000, le=200000)
    max_output_tokens: int = Field(default=4000, ge=256, le=16000)


class Progress(BaseModel):
    phase: str
    percent: int


class Job(BaseModel):
    model_config = ConfigDict(extra="allow")
    job_id: str
    kind: Literal["scan", "review", "provider_check"]
    parent_job_id: str | None = None
    status: Status
    progress: Progress | None = None
    submitted_at: str
    started_at: str | None = None
    finished_at: str | None = None
    error: str | None = None
    config: dict[str, Any]
    source: dict[str, Any]
    latest_review_id: str | None = None
    steps: list[dict[str, Any]] = Field(default_factory=list)


class JobList(BaseModel):
    items: list[Job]
    total: int
    page: int
    limit: int


class Submission(BaseModel):
    job_id: str
    status: str
    run_id: str | None = None


class Issue(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    tool: str
    type: str
    message: str
    severity: Literal["critical", "high", "medium", "low"]
    file: str
    line: int
    rule_id: str
    source_hash: str | None = None
    suggestion: str | None = None
    fingerprint: str | None = None
    logical_id: str | None = None
    family: str | None = None
    cwe: str | list[str] | None = None
    analysis_kind: str | None = None
    end_line: int | None = None
    rule_digest: str | None = None
    dependency: dict[str, Any] | None = None


class Coverage(BaseModel):
    model_config = ConfigDict(extra="allow")
    tool: str
    status: str
    files_discovered: int = 0
    files_scanned: int = 0
    files_skipped: int = 0
    errors: list[str] = Field(default_factory=list)
    version: str = "unknown"
    languages: list[str] = Field(default_factory=list)


class FileIssues(BaseModel):
    path: str
    issues: list[Issue]


class ScanReport(BaseModel):
    model_config = ConfigDict(extra="allow")
    schema_version: str = "2.0"
    job_id: str
    meta: dict[str, Any]
    summary: dict[str, int]
    files: list[FileIssues]
    coverage: list[Coverage] = Field(default_factory=list)
    ai_analysis: dict[str, Any] | None = None
    project_id: str | None = None
    stream: str | None = None
    profiles: dict[str, Any] | None = None
    baseline: dict[str, Any] | None = None
    report_hash: str | None = None


class ProjectInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=160)
    kind: Literal["zip"] = "zip"


class Project(BaseModel):
    id: str
    name: str
    kind: Literal["zip", "github"]
    repository_key: str | None = None
    created_at: str


class ProjectList(BaseModel):
    items: list[Project]
    total: int
    page: int
    limit: int


class TriageInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal["open", "confirmed", "dismissed"]
    expected_revision: int = Field(ge=0)
    reason: str | None = Field(default=None, max_length=4000)
    category: Literal["false_positive", "accepted_risk", "not_actionable"] | None = None


class NoteInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    body: str = Field(min_length=1, max_length=10000)


class ProposalSelection(BaseModel):
    proposal_ids: list[str] = Field(min_length=1, max_length=100)


class TriageDecision(BaseModel):
    model_config = ConfigDict(extra='allow')
    status: Literal['open', 'confirmed', 'dismissed']
    revision: int
    reason: str | None = None
    category: str | None = None
    requires_reconfirmation: bool = False


class ProjectFinding(BaseModel):
    model_config = ConfigDict(extra='allow')
    id: str
    logical_id: str
    project_id: str
    fingerprint: str
    file: str
    line: int
    rule_id: str
    tool: str
    message: str
    severity: str
    triage: TriageDecision
    notes: list[dict[str, Any]]
    history: list[dict[str, Any]]
    latest_occurrence: dict[str, Any]


class ProjectFindingList(BaseModel):
    items: list[ProjectFinding]
    total: int
    page: int
    limit: int


class ComparisonItem(BaseModel):
    classification: Literal['new', 'existing', 'resolved', 'not_assessed', 'ambiguous']
    finding: dict[str, Any]
    baseline_finding: dict[str, Any] | None = None
    reason: str | None = None


class Comparison(BaseModel):
    has_baseline: bool
    current: dict[str, str]
    baseline: dict[str, str] | None = None
    items: list[ComparisonItem]
    counts: dict[str, int]
    comparability_reasons: list[str]
    status: Literal['completed', 'incomplete']
