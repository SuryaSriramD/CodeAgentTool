"""Data models and schema definitions for reports and API responses."""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import json


class JobStatus(str, Enum):
    """Job execution status."""
    QUEUED = "queued"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"
    EXPIRED = "expired"


class JobPhase(str, Enum):
    """Job execution phases."""
    CLONE = "clone"
    ANALYZE_SEMGREP = "analyze:semgrep"
    ANALYZE_BANDIT = "analyze:bandit"
    ANALYZE_DEPCHECK = "analyze:depcheck"
    MERGE = "merge"
    WRITE = "write"


class Severity(str, Enum):
    """Issue severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class RepoInfo:
    """Repository source information."""
    source: str  # "github" or "zip"
    url: Optional[str] = None
    ref: Optional[str] = None
    commit: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Issue:
    """Normalized security issue/vulnerability."""
    tool: str
    type: str
    message: str
    severity: Severity
    file: str
    line: int
    rule_id: str
    suggestion: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['severity'] = self.severity.value
        return result


@dataclass
class FileIssues:
    """Issues grouped by file."""
    path: str
    issues: List[Issue]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "issues": [issue.to_dict() for issue in self.issues]
        }


@dataclass
class SeveritySummary:
    """Summary of issues by severity."""
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    
    def total(self) -> int:
        return self.critical + self.high + self.medium + self.low
    
    def add_severity(self, severity: Severity) -> None:
        """Add one issue of the given severity."""
        if severity == Severity.CRITICAL:
            self.critical += 1
        elif severity == Severity.HIGH:
            self.high += 1
        elif severity == Severity.MEDIUM:
            self.medium += 1
        elif severity == Severity.LOW:
            self.low += 1
    
    def to_dict(self) -> Dict[str, int]:
        return asdict(self)


@dataclass
class ReportMetadata:
    """Report metadata."""
    tools: List[str]
    repo: RepoInfo
    generated_at: str
    duration_ms: int
    labels: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tools": self.tools,
            "repo": self.repo.to_dict(),
            "generated_at": self.generated_at,
            "duration_ms": self.duration_ms,
            "labels": self.labels
        }


@dataclass
class Report:
    """Complete security scan report."""
    job_id: str
    meta: ReportMetadata
    summary: SeveritySummary
    files: List[FileIssues]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "meta": self.meta.to_dict(),
            "summary": self.summary.to_dict(),
            "files": [file_issue.to_dict() for file_issue in self.files]
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


@dataclass
class JobProgress:
    """Job execution progress information."""
    phase: JobPhase
    percent: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase": self.phase.value,
            "percent": self.percent
        }


@dataclass
class JobInfo:
    """Complete job information."""
    job_id: str
    status: JobStatus
    progress: Optional[JobProgress]
    submitted_at: str
    started_at: Optional[str]
    finished_at: Optional[str]
    error: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "job_id": self.job_id,
            "status": self.status.value,
            "submitted_at": self.submitted_at,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "error": self.error
        }
        
        if self.progress:
            result["progress"] = self.progress.to_dict()
        
        return result


@dataclass
class WebhookConfig:
    """Webhook configuration."""
    id: str
    url: str
    events: List[str]
    secret: Optional[str]
    created_at: str
    active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "url": self.url,
            "events": self.events,
            "secret": "***" if self.secret else None,  # Don't expose secret
            "created_at": self.created_at,
            "active": self.active
        }


@dataclass
class WebhookPayload:
    """Webhook delivery payload."""
    job_id: str
    repo: RepoInfo
    summary: SeveritySummary
    report_url: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "repo": self.repo.to_dict(),
            "summary": self.summary.to_dict(),
            "report_url": self.report_url
        }


@dataclass
class AnalyzerConfig:
    """Configuration for analyzers."""
    defaults: List[str]
    rulesets: Dict[str, List[str]]
    allow_list: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ErrorResponse:
    """Standard error response."""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "error": {
                "code": self.code,
                "message": self.message
            }
        }
        
        if self.details:
            result["error"]["details"] = self.details
        
        return result


@dataclass
class AnalyzeRequest:
    """Request model for analyze endpoints."""
    github_url: Optional[str] = None
    ref: Optional[str] = None
    commit: Optional[str] = None
    file: Optional[bytes] = None
    include: Optional[str] = None
    exclude: Optional[str] = None
    analyzers: Optional[str] = None
    timeout_sec: Optional[int] = None
    labels: Optional[str] = None
    
    def get_analyzers_list(self) -> List[str]:
        """Parse analyzers CSV string into list."""
        if not self.analyzers:
            return []
        return [a.strip() for a in self.analyzers.split(',') if a.strip()]
    
    def get_include_patterns(self) -> List[str]:
        """Parse include CSV string into list."""
        if not self.include:
            return []
        return [p.strip() for p in self.include.split(',') if p.strip()]
    
    def get_exclude_patterns(self) -> List[str]:
        """Parse exclude CSV string into list.""" 
        if not self.exclude:
            return []
        return [p.strip() for p in self.exclude.split(',') if p.strip()]
    
    def get_labels_list(self) -> List[str]:
        """Parse labels CSV string into list."""
        if not self.labels:
            return []
        return [l.strip() for l in self.labels.split(',') if l.strip()]


@dataclass
class AnalyzeResponse:
    """Response model for analyze endpoints."""
    job_id: str
    status: Optional[str] = None
    summary: Optional[SeveritySummary] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {"job_id": self.job_id}
        
        if self.status:
            result["status"] = self.status
        
        if self.summary:
            result["summary"] = self.summary.to_dict()
        
        return result


@dataclass
class ReportListItem:
    """Report item in paginated list."""
    job_id: str
    repo_url: Optional[str]
    generated_at: str
    summary: SeveritySummary
    tools: List[str]
    labels: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "repo_url": self.repo_url,
            "generated_at": self.generated_at,
            "summary": self.summary.to_dict(),
            "tools": self.tools,
            "labels": self.labels
        }


@dataclass
class ReportListResponse:
    """Paginated reports response."""
    items: List[ReportListItem]
    page: int
    limit: int
    total: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": [item.to_dict() for item in self.items],
            "page": self.page,
            "limit": self.limit,
            "total": self.total
        }


@dataclass
class ToolInfo:
    """Tool/analyzer information."""
    name: str
    version: str
    available: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ToolsResponse:
    """Response for /tools endpoint."""
    available: List[str]
    default: List[str]
    versions: Dict[str, str]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class HealthResponse:
    """Response for /health endpoint."""
    status: str
    version: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ReportBuilder:
    """Helper class to build reports from analyzer results."""
    
    def __init__(self):
        self.issues: List[Issue] = []
        self.tools_used: List[str] = []
    
    def add_analyzer_result(self, result: Any) -> None:
        """Add results from an analyzer."""
        # Import here to avoid circular imports
        # result should be an AnalyzerResult object
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Adding analyzer result: tool={result.tool_name}, success={result.success}, issues_count={len(result.issues)}")
        
        if result.success:
            self.tools_used.append(result.tool_name)
            
            # Convert analyzer issues to report issues
            for analyzer_issue in result.issues:
                try:
                    issue = Issue(
                        tool=analyzer_issue.tool,
                        type=analyzer_issue.type,
                        message=analyzer_issue.message,
                        severity=Severity(analyzer_issue.severity.value),
                        file=analyzer_issue.file,
                        line=analyzer_issue.line,
                        rule_id=analyzer_issue.rule_id,
                        suggestion=analyzer_issue.suggestion
                    )
                    self.issues.append(issue)
                    logger.debug(f"Added issue: {analyzer_issue.type} in {analyzer_issue.file}")
                except Exception as e:
                    logger.error(f"Failed to convert issue: {e}", exc_info=True)
    
    def build_report(
        self,
        job_id: str,
        repo_info: RepoInfo,
        labels: List[str],
        start_time: datetime,
        end_time: datetime
    ) -> Report:
        """Build final report."""
        
        # Group issues by file
        files_dict: Dict[str, List[Issue]] = {}
        for issue in self.issues:
            if issue.file not in files_dict:
                files_dict[issue.file] = []
            files_dict[issue.file].append(issue)
        
        # Create FileIssues objects
        files = [
            FileIssues(path=path, issues=issues)
            for path, issues in sorted(files_dict.items())
        ]
        
        # Calculate summary
        summary = SeveritySummary()
        for issue in self.issues:
            summary.add_severity(issue.severity)
        
        # Create metadata
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        meta = ReportMetadata(
            tools=self.tools_used,
            repo=repo_info,
            generated_at=end_time.isoformat(),
            duration_ms=duration_ms,
            labels=labels
        )
        
        return Report(
            job_id=job_id,
            meta=meta,
            summary=summary,
            files=files
        )