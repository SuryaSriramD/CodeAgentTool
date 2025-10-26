"""
Integration tests for AgentBridge.
Tests the bridge between vulnerability scanner and CodeAgent AI.
"""

import pytest
import sys
import os
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from integration.agent_bridge import AgentBridge


class TestAgentBridgeInitialization:
    """Test AgentBridge initialization."""
    
    def test_init_default_config(self):
        """Test initialization with default configuration."""
        bridge = AgentBridge()
        
        assert bridge.config_dir is not None
        assert bridge.config_path.exists()
        assert bridge.config_phase_path.exists()
        assert bridge.config_role_path.exists()
    
    def test_init_custom_config(self):
        """Test initialization with custom configuration directory."""
        config_dir = Path(__file__).parent.parent.parent / "CompanyConfig" / "Default"
        bridge = AgentBridge(config_dir=str(config_dir))
        
        assert bridge.config_dir == config_dir
        assert bridge.config_path == config_dir / "ChatChainConfig.json"
    
    def test_config_files_exist(self):
        """Test that all required configuration files exist."""
        bridge = AgentBridge()
        
        assert bridge.config_path.is_file(), "ChatChainConfig.json not found"
        assert bridge.config_phase_path.is_file(), "PhaseConfig.json not found"
        assert bridge.config_role_path.is_file(), "RoleConfig.json not found"


class TestPromptCreation:
    """Test prompt generation for AI analysis."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.bridge = AgentBridge()
    
    def test_create_review_prompt_single_issue(self):
        """Test prompt creation with a single vulnerability."""
        file_path = "test.py"
        issues = [
            {
                "severity": "high",
                "type": "SQL Injection",
                "line": 42,
                "tool": "semgrep",
                "message": "Potential SQL injection vulnerability",
                "suggestion": "Use parameterized queries"
            }
        ]
        file_content = "def query(user_input):\n    sql = f'SELECT * FROM users WHERE id = {user_input}'"
        
        prompt = self.bridge._create_review_prompt(file_path, issues, file_content)
        
        assert "test.py" in prompt
        assert "SQL Injection" in prompt
        assert "high" in prompt.lower()
        assert "Line: 42" in prompt
        assert "semgrep" in prompt
        assert "Potential SQL injection" in prompt
        assert file_content in prompt
    
    def test_create_review_prompt_multiple_issues(self):
        """Test prompt creation with multiple vulnerabilities."""
        file_path = "app.py"
        issues = [
            {
                "severity": "critical",
                "type": "Command Injection",
                "line": 10,
                "tool": "bandit",
                "message": "Command injection risk",
                "suggestion": "Avoid shell=True"
            },
            {
                "severity": "high",
                "type": "XSS",
                "line": 25,
                "tool": "semgrep",
                "message": "Reflected XSS vulnerability",
                "suggestion": "Escape user input"
            }
        ]
        file_content = "import subprocess\nsubprocess.call(user_input, shell=True)"
        
        prompt = self.bridge._create_review_prompt(file_path, issues, file_content)
        
        assert "1. CRITICAL - Command Injection" in prompt
        assert "2. HIGH - XSS" in prompt
        assert "Line: 10" in prompt
        assert "Line: 25" in prompt
    
    def test_create_review_prompt_no_line_number(self):
        """Test prompt creation when line number is missing."""
        file_path = "test.py"
        issues = [
            {
                "severity": "medium",
                "type": "Weak Crypto",
                "tool": "semgrep",
                "message": "MD5 is cryptographically weak",
                "suggestion": "Use SHA-256 or better"
            }
        ]
        file_content = "import hashlib\nhashlib.md5()"
        
        prompt = self.bridge._create_review_prompt(file_path, issues, file_content)
        
        assert "Line: N/A" in prompt
        assert "Weak Crypto" in prompt


class TestVulnerabilityProcessing:
    """Test vulnerability report processing."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.bridge = AgentBridge()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_process_empty_report(self):
        """Test processing an empty vulnerability report."""
        job_id = "test_job_001"
        report = {
            "files": []
        }
        
        result = await self.bridge.process_vulnerabilities(
            job_id=job_id,
            report=report,
            workspace_path=self.temp_dir
        )
        
        assert result["job_id"] == job_id
        assert result["enhanced_issues"] == []
        assert "summary" in result
    
    @pytest.mark.asyncio
    async def test_process_report_no_issues(self):
        """Test processing report with files but no issues."""
        job_id = "test_job_002"
        report = {
            "files": [
                {
                    "path": "clean_file.py",
                    "issues": []
                }
            ]
        }
        
        result = await self.bridge.process_vulnerabilities(
            job_id=job_id,
            report=report,
            workspace_path=self.temp_dir
        )
        
        assert result["job_id"] == job_id
        assert len(result["enhanced_issues"]) == 0
    
    @pytest.mark.asyncio
    async def test_process_report_low_severity_only(self):
        """Test that low severity issues are not sent to AI."""
        job_id = "test_job_003"
        
        # Create test file
        test_file = os.path.join(self.temp_dir, "test.py")
        with open(test_file, "w") as f:
            f.write("# Some code")
        
        report = {
            "files": [
                {
                    "path": "test.py",
                    "issues": [
                        {
                            "severity": "low",
                            "type": "Info",
                            "line": 1,
                            "tool": "semgrep",
                            "message": "Low priority issue"
                        }
                    ]
                }
            ]
        }
        
        result = await self.bridge.process_vulnerabilities(
            job_id=job_id,
            report=report,
            workspace_path=self.temp_dir
        )
        
        # Low severity issues should not be AI-analyzed
        assert len(result["enhanced_issues"]) == 0
    
    @pytest.mark.asyncio
    async def test_process_report_file_not_found(self):
        """Test processing when referenced file doesn't exist."""
        job_id = "test_job_004"
        report = {
            "files": [
                {
                    "path": "nonexistent.py",
                    "issues": [
                        {
                            "severity": "critical",
                            "type": "Bug",
                            "line": 1,
                            "tool": "test",
                            "message": "Test issue"
                        }
                    ]
                }
            ]
        }
        
        # Should handle missing file gracefully
        with patch.object(self.bridge, '_analyze_with_ai', new_callable=AsyncMock) as mock_analyze:
            mock_analyze.return_value = {
                'error': 'File not found',
                'file': 'nonexistent.py'
            }
            
            result = await self.bridge.process_vulnerabilities(
                job_id=job_id,
                report=report,
                workspace_path=self.temp_dir
            )
            
            assert result["job_id"] == job_id


class TestEnhancedSummary:
    """Test summary generation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.bridge = AgentBridge()
    
    def test_create_enhanced_summary_empty(self):
        """Test summary creation with no issues."""
        enhanced_issues = []
        
        summary = self.bridge._create_enhanced_summary(enhanced_issues)
        
        assert "files_analyzed" in summary
        assert summary["files_analyzed"] == 0
        assert summary["issues_analyzed"] == 0
        assert summary["ai_fixes_generated"] == 0
        assert summary["status"] == "complete"
    
    def test_create_enhanced_summary_with_issues(self):
        """Test summary creation with analyzed issues."""
        enhanced_issues = [
            {
                "file": "test1.py",
                "original_issues": [{"severity": "high", "type": "SQL Injection"}],
                "ai_analysis": {
                    "analysis": "SQL injection found",
                    "suggested_fix": "Use parameterized queries"
                }
            },
            {
                "file": "test2.py",
                "original_issues": [{"severity": "critical", "type": "Command Injection"}],
                "ai_analysis": {
                    "analysis": "Command injection risk",
                    "suggested_fix": "Avoid shell=True"
                }
            }
        ]
        
        summary = self.bridge._create_enhanced_summary(enhanced_issues)
        
        assert summary["files_analyzed"] == 2
        assert summary["issues_analyzed"] == 2
        assert summary["ai_fixes_generated"] == 2
        assert summary["status"] == "complete"


class TestRecommendationExtraction:
    """Test extraction of AI recommendations."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.bridge = AgentBridge()
    
    def test_extract_recommendations_no_warehouse(self):
        """Test extraction when warehouse directory doesn't exist."""
        fake_path = Path("/nonexistent/warehouse")
        
        result = self.bridge._extract_recommendations(fake_path)
        
        assert "analysis" in result
        assert "fix" in result
        assert "explanation" in result
    
    def test_extract_recommendations_with_mock_files(self):
        """Test extraction with mocked warehouse files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            warehouse_path = Path(temp_dir)
            
            # Create mock security test file
            test_file = warehouse_path / "TestVulnerabilitySummary.txt"
            test_file.write_text("Security Analysis:\nVulnerability found in line 42")
            
            result = self.bridge._extract_recommendations(warehouse_path)
            
            assert "analysis" in result
            assert "fix" in result


class TestErrorHandling:
    """Test error handling in AgentBridge."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.bridge = AgentBridge()
    
    @pytest.mark.asyncio
    async def test_analyze_with_ai_exception(self):
        """Test that exceptions in AI analysis are handled gracefully."""
        job_id = "test_job_error"
        file_path = "test.py"
        issues = [{"severity": "high", "type": "Test", "tool": "test", "message": "Test"}]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test file
            test_file = os.path.join(temp_dir, "test.py")
            with open(test_file, "w") as f:
                f.write("print('test')")
            
            # Mock ChatChain to raise an exception
            with patch('integration.agent_bridge.ChatChain') as mock_chain:
                mock_chain.side_effect = Exception("AI service unavailable")
                
                result = await self.bridge._analyze_with_ai(
                    job_id=job_id,
                    file_path="test.py",
                    issues=issues,
                    workspace_path=temp_dir
                )
                
                assert "error" in result
                assert "AI service unavailable" in result["error"]
                assert result["file"] == file_path


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
