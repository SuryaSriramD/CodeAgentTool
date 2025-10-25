"""Base analyzer class and common interfaces."""

import abc
import logging
import subprocess
import tempfile
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json


class Severity(str, Enum):
    """Issue severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Issue:
    """Normalized vulnerability/issue finding."""
    tool: str
    type: str
    message: str
    severity: Severity
    file: str
    line: int
    rule_id: str
    suggestion: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "tool": self.tool,
            "type": self.type,
            "message": self.message,
            "severity": self.severity.value,
            "file": self.file,
            "line": self.line,
            "rule_id": self.rule_id,
            "suggestion": self.suggestion
        }


@dataclass
class AnalyzerResult:
    """Result from running an analyzer."""
    tool_name: str
    success: bool
    issues: List[Issue]
    duration_ms: int
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "tool_name": self.tool_name,
            "success": self.success,
            "issues": [issue.to_dict() for issue in self.issues],
            "duration_ms": self.duration_ms,
            "error_message": self.error_message
        }


class BaseAnalyzer(abc.ABC):
    """Abstract base class for all security analyzers."""
    
    def __init__(self, timeout_sec: int = 300):
        self.timeout_sec = timeout_sec
        self.logger = logging.getLogger(f"analyzer.{self.name}")
    
    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Analyzer name (e.g., 'semgrep', 'bandit')."""
        pass
    
    @property
    @abc.abstractmethod
    def version(self) -> str:
        """Get analyzer version."""
        pass
    
    @abc.abstractmethod
    def is_applicable(self, workspace_path: str) -> bool:
        """Check if this analyzer should run on the given workspace."""
        pass
    
    @abc.abstractmethod
    def run_analysis(self, workspace_path: str, **kwargs) -> AnalyzerResult:
        """Run the analyzer on the workspace and return normalized results."""
        pass
    
    def _run_command(self, cmd: List[str], cwd: str, capture_output: bool = True) -> subprocess.CompletedProcess:
        """Helper to run subprocess with timeout and logging."""
        self.logger.debug(f"Running command: {' '.join(cmd)} in {cwd}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=capture_output,
                text=True,
                timeout=self.timeout_sec,
                check=False
            )
            
            if result.returncode != 0:
                self.logger.warning(f"Command failed with code {result.returncode}: {result.stderr}")
            
            return result
            
        except subprocess.TimeoutExpired as e:
            self.logger.error(f"Command timed out after {self.timeout_sec}s: {' '.join(cmd)}")
            raise
        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            raise
    
    def _parse_severity(self, raw_severity: str) -> Severity:
        """Parse and normalize severity from tool output."""
        severity_map = {
            # Common mappings
            "critical": Severity.CRITICAL,
            "high": Severity.HIGH,
            "medium": Severity.MEDIUM,
            "low": Severity.LOW,
            "info": Severity.LOW,
            "warning": Severity.MEDIUM,
            "error": Severity.HIGH,
            # Numeric mappings
            "1": Severity.LOW,
            "2": Severity.MEDIUM,
            "3": Severity.HIGH,
            "4": Severity.CRITICAL,
        }
        
        normalized = raw_severity.lower().strip()
        return severity_map.get(normalized, Severity.MEDIUM)
    
    def _normalize_file_path(self, file_path: str, workspace_path: str) -> str:
        """Normalize file path to be relative to workspace."""
        import os
        
        if os.path.isabs(file_path):
            try:
                return os.path.relpath(file_path, workspace_path)
            except ValueError:
                # Can't make relative, use as-is
                return file_path
        return file_path


class AnalyzerRegistry:
    """Registry for managing available analyzers."""
    
    def __init__(self):
        self._analyzers: Dict[str, type[BaseAnalyzer]] = {}
    
    def register(self, analyzer_class: type[BaseAnalyzer]):
        """Register an analyzer class."""
        # Get name from class instance (need to create temp instance)
        temp_instance = analyzer_class()
        name = temp_instance.name
        self._analyzers[name] = analyzer_class
        logging.info(f"Registered analyzer: {name}")
    
    def get_analyzer(self, name: str, **kwargs) -> Optional[BaseAnalyzer]:
        """Get analyzer instance by name."""
        analyzer_class = self._analyzers.get(name)
        if analyzer_class:
            return analyzer_class(**kwargs)
        return None
    
    def list_analyzers(self) -> List[str]:
        """List all registered analyzer names."""
        return list(self._analyzers.keys())
    
    def get_versions(self) -> Dict[str, str]:
        """Get version info for all analyzers."""
        versions = {}
        for name, analyzer_class in self._analyzers.items():
            try:
                temp_instance = analyzer_class()
                versions[name] = temp_instance.version
            except Exception as e:
                logging.warning(f"Could not get version for {name}: {e}")
                versions[name] = "unknown"
        return versions


# Global registry instance
analyzer_registry = AnalyzerRegistry()