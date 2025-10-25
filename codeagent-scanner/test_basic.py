"""Basic tests for the CodeAgent Scanner API."""

import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Test the basic imports work
def test_imports():
    """Test that all main modules can be imported."""
    from analyzers.base import BaseAnalyzer, analyzer_registry
    from ingestion.fetch_repo import RepoFetcher
    from ingestion.sanitize import WorkspaceSanitizer
    from pipeline.orchestrator import JobOrchestrator
    from pipeline.report_schema import Report, Issue, Severity
    
    assert BaseAnalyzer is not None
    assert analyzer_registry is not None
    assert RepoFetcher is not None
    assert WorkspaceSanitizer is not None
    assert JobOrchestrator is not None
    assert Report is not None
    assert Issue is not None
    assert Severity is not None


def test_analyzer_registry():
    """Test analyzer registry functionality."""
    from analyzers.base import analyzer_registry
    
    # Should have registered analyzers
    analyzers = analyzer_registry.list_analyzers()
    assert len(analyzers) > 0
    assert "semgrep" in analyzers or "bandit" in analyzers or "depcheck" in analyzers
    
    # Should be able to get versions
    versions = analyzer_registry.get_versions()
    assert isinstance(versions, dict)


def test_workspace_sanitizer():
    """Test workspace sanitization."""
    from ingestion.sanitize import WorkspaceSanitizer
    
    sanitizer = WorkspaceSanitizer()
    
    # Test ignore patterns
    assert sanitizer._should_ignore_directory("node_modules")
    assert sanitizer._should_ignore_directory(".git")
    assert not sanitizer._should_ignore_directory("src")
    
    assert sanitizer._should_ignore_file("test.pyc", "/tmp/test.pyc")
    assert sanitizer._should_ignore_file(".hidden", "/tmp/.hidden")
    assert not sanitizer._should_ignore_file("main.py", "/tmp/main.py")


def test_repo_fetcher_validation():
    """Test URL validation in RepoFetcher."""
    from ingestion.fetch_repo import RepoFetcher, RepoFetchError
    
    with tempfile.TemporaryDirectory() as temp_dir:
        fetcher = RepoFetcher(temp_dir)
        
        # Valid GitHub URL should not raise
        try:
            fetcher._validate_github_url("https://github.com/user/repo")
        except RepoFetchError:
            pytest.fail("Valid GitHub URL should not raise exception")
        
        # Invalid URLs should raise
        with pytest.raises(RepoFetchError):
            fetcher._validate_github_url("ftp://invalid.com/repo")
        
        with pytest.raises(RepoFetchError):
            fetcher._validate_github_url("https://evil.com/repo")


def test_severity_enum():
    """Test severity enumeration."""
    from pipeline.report_schema import Severity
    
    assert Severity.CRITICAL == "critical"
    assert Severity.HIGH == "high"
    assert Severity.MEDIUM == "medium"
    assert Severity.LOW == "low"


def test_report_building():
    """Test report building functionality."""
    from pipeline.report_schema import ReportBuilder, Issue, Severity, RepoInfo
    from datetime import datetime
    
    builder = ReportBuilder()
    
    # Create mock analyzer result
    mock_result = MagicMock()
    mock_result.success = True
    mock_result.tool_name = "test_tool"
    mock_result.issues = []
    
    builder.add_analyzer_result(mock_result)
    
    # Build report
    repo_info = RepoInfo(source="github", url="https://github.com/test/repo")
    start_time = datetime.now()
    end_time = datetime.now()
    
    report = builder.build_report(
        job_id="test-job",
        repo_info=repo_info,
        labels=["test"],
        start_time=start_time,
        end_time=end_time
    )
    
    assert report.job_id == "test-job"
    assert report.meta.repo.source == "github"
    assert report.meta.labels == ["test"]


if __name__ == "__main__":
    pytest.main([__file__])