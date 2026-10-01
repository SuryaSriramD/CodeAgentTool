"""Analyzer contracts. Findings and incomplete analysis are separate outcomes."""
from __future__ import annotations
import abc
import logging
import os
import signal
import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from pathlib import Path


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Issue:
    tool: str
    type: str
    message: str
    severity: Severity
    file: str
    line: int
    rule_id: str
    suggestion: Optional[str] = None
    id: Optional[str] = None
    source_hash: Optional[str] = None
    family: Optional[str] = None
    cwe: Optional[str] = None
    analysis_kind: str = "structural"
    end_line: Optional[int] = None
    end_column: Optional[int] = None
    rule_revision: str = "1"
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    dependency: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {**self.__dict__, "severity": self.severity.value}


@dataclass
class AnalyzerResult:
    tool_name: str
    success: bool
    issues: List[Issue]
    duration_ms: int
    error_message: Optional[str] = None
    status: Optional[str] = None
    coverage: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.status is None:
            self.status = "completed" if self.success else "failed"

    def to_dict(self):
        return {"tool_name": self.tool_name, "success": self.success,
                "issues": [i.to_dict() for i in self.issues], "duration_ms": self.duration_ms,
                "error_message": self.error_message, "status": self.status, "coverage": self.coverage}


class AnalysisCancelled(RuntimeError):
    pass


def terminate_process_group(process):
    """Stop grandchildren even if the group leader has already exited."""
    try:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGTERM)
        else:
            process.terminate()
        process.wait(timeout=1)
    except (ProcessLookupError, subprocess.TimeoutExpired):
        pass
    finally:
        try:
            if os.name == "posix":
                os.killpg(process.pid, signal.SIGKILL)
            elif process.poll() is None:
                process.kill()
        except ProcessLookupError:
            pass
        process.wait()


class BaseAnalyzer(abc.ABC):
    def __init__(self, timeout_sec=300, cancel=None):
        self.timeout_sec = timeout_sec
        self.cancel = cancel or (lambda: False)
        self.logger = logging.getLogger(f"analyzer.{self.name}")

    @property
    @abc.abstractmethod
    def name(self): ...

    @property
    @abc.abstractmethod
    def version(self): ...

    @abc.abstractmethod
    def is_applicable(self, workspace_path): ...

    @abc.abstractmethod
    def run_analysis(self, workspace_path, **kwargs): ...

    def _run_command(self, cmd, cwd, capture_output=True, env=None):
        if self.cancel():
            raise AnalysisCancelled("Analysis cancelled before tool launch")
        if not hasattr(self, "_command_deadline"):
            self._command_deadline = time.monotonic() + self.timeout_sec
        process = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True, encoding="utf-8", errors="replace", env=env,
                                   start_new_session=(os.name == "posix"))
        try:
            while True:
                if self.cancel():
                    raise AnalysisCancelled("Analysis cancelled")
                if time.monotonic() >= self._command_deadline:
                    raise subprocess.TimeoutExpired(cmd, self.timeout_sec)
                try:
                    out, err = process.communicate(timeout=0.1)
                    return subprocess.CompletedProcess(cmd, process.returncode, out, err)
                except subprocess.TimeoutExpired:
                    continue
        except BaseException:
            terminate_process_group(process)
            process.communicate()
            raise

    def _parse_severity(self, raw):
        return {"critical": Severity.CRITICAL, "high": Severity.HIGH, "error": Severity.HIGH,
                "medium": Severity.MEDIUM, "moderate": Severity.MEDIUM, "warning": Severity.MEDIUM,
                "low": Severity.LOW, "info": Severity.LOW,
                "1": Severity.LOW, "2": Severity.MEDIUM, "3": Severity.HIGH,
                "4": Severity.CRITICAL}.get(str(raw).strip().lower(), Severity.MEDIUM)

    def _normalize_file_path(self, file_path, workspace_path):
        root = Path(workspace_path).resolve()
        path = Path(file_path)
        return (path if path.is_absolute() else root / path).resolve().relative_to(root).as_posix()


class AnalyzerRegistry:
    def __init__(self):
        self._analyzers = {}

    def register(self, klass):
        self._analyzers[klass().name] = klass

    def get_analyzer(self, name, **kwargs):
        klass = self._analyzers.get("depcheck" if name == "trivy" else name)
        return klass(**kwargs) if klass else None

    def list_analyzers(self):
        return list(self._analyzers)

    def get_versions(self):
        return {name: klass().version for name, klass in self._analyzers.items()}


analyzer_registry = AnalyzerRegistry()
