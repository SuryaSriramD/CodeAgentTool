"""Semgrep security analyzer runner."""

import json
import os
import subprocess
import tempfile
import time
from typing import List, Dict, Any, Optional

from .base import BaseAnalyzer, AnalyzerResult, Issue, Severity, analyzer_registry


class SemgrepAnalyzer(BaseAnalyzer):
    """Semgrep static analysis security scanner."""
    
    def __init__(self, timeout_sec: int = 300, rulesets: Optional[List[str]] = None):
        super().__init__(timeout_sec)
        self.rulesets = rulesets or ["p/owasp-top-ten", "p/security-audit"]
        
    @property
    def name(self) -> str:
        return "semgrep"
    
    @property
    def version(self) -> str:
        """Get Semgrep version."""
        try:
            result = subprocess.run(
                ["semgrep", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # Parse version from output like "1.81.0"
                version_line = result.stdout.strip().split('\n')[0]
                return version_line
            return "unknown"
        except Exception:
            return "unknown"
    
    def is_applicable(self, workspace_path: str) -> bool:
        """Check if Semgrep should run on this workspace."""
        # Semgrep supports many languages, check for common source file extensions
        supported_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go',
            '.c', '.cpp', '.cc', '.cxx', '.h', '.hpp',
            '.rb', '.php', '.scala', '.kt', '.swift', '.cs',
            '.yaml', '.yml', '.json', '.dockerfile'
        }
        
        try:
            for root, dirs, files in os.walk(workspace_path):
                # Skip common ignore directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__']]
                
                for file in files:
                    _, ext = os.path.splitext(file)
                    if ext.lower() in supported_extensions:
                        return True
            return False
        except Exception as e:
            self.logger.error(f"Error checking workspace applicability: {e}")
            return False
    
    def run_analysis(self, workspace_path: str, **kwargs) -> AnalyzerResult:
        """Run Semgrep analysis on the workspace."""
        start_time = time.time()
        issues = []
        error_message = None
        
        try:
            # Create temporary file for output
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as tmp_file:
                output_file = tmp_file.name
            
            # Build Semgrep command
            cmd = [
                "semgrep",
                "--config=auto",  # Use registry rules
                "--json",
                f"--output={output_file}",
                "--quiet",
                "--no-git-ignore",  # We handle ignores ourselves
                workspace_path
            ]
            
            # Add custom rulesets if specified
            if self.rulesets:
                cmd = [
                    "semgrep",
                    "--json", 
                    f"--output={output_file}",
                    "--quiet",
                    "--no-git-ignore"
                ]
                
                for ruleset in self.rulesets:
                    cmd.extend(["--config", ruleset])
                
                cmd.append(workspace_path)
            
            self.logger.info(f"Running Semgrep with command: {' '.join(cmd)}")
            
            # Run Semgrep
            result = self._run_command(cmd, workspace_path, capture_output=True)
            
            # Parse results
            if os.path.exists(output_file):
                issues = self._parse_semgrep_output(output_file, workspace_path)
                os.unlink(output_file)  # Clean up temp file
            
            # Semgrep returns non-zero when findings are found, which is expected
            success = result.returncode in [0, 1]  # 0 = no findings, 1 = findings found
            
            if result.returncode > 1:
                error_message = f"Semgrep failed with code {result.returncode}: {result.stderr}"
                success = False
            
        except subprocess.TimeoutExpired:
            error_message = f"Semgrep analysis timed out after {self.timeout_sec} seconds"
            success = False
        except Exception as e:
            error_message = f"Semgrep analysis failed: {str(e)}"
            success = False
        finally:
            # Clean up temp file if it exists
            if 'output_file' in locals() and os.path.exists(output_file):
                try:
                    os.unlink(output_file)
                except Exception:
                    pass
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        return AnalyzerResult(
            tool_name=self.name,
            success=success,
            issues=issues,
            duration_ms=duration_ms,
            error_message=error_message
        )
    
    def _parse_semgrep_output(self, output_file: str, workspace_path: str) -> List[Issue]:
        """Parse Semgrep JSON output into normalized Issues."""
        issues = []
        
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Semgrep JSON format has 'results' array
            results = data.get('results', [])
            
            for finding in results:
                try:
                    issue = self._convert_semgrep_finding(finding, workspace_path)
                    if issue:
                        issues.append(issue)
                except Exception as e:
                    self.logger.warning(f"Failed to parse Semgrep finding: {e}")
                    continue
        
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse Semgrep JSON output: {e}")
        except Exception as e:
            self.logger.error(f"Error reading Semgrep output: {e}")
        
        return issues
    
    def _convert_semgrep_finding(self, finding: Dict[str, Any], workspace_path: str) -> Optional[Issue]:
        """Convert a single Semgrep finding to normalized Issue."""
        try:
            # Extract basic information
            check_id = finding.get('check_id', 'unknown')
            message = finding.get('message', 'Security issue detected')
            
            # Get file path and line number
            path = finding.get('path', '')
            start_line = finding.get('start', {}).get('line', 1)
            
            # Normalize file path
            normalized_path = self._normalize_file_path(path, workspace_path)
            
            # Determine severity from metadata or rule ID
            severity = self._determine_semgrep_severity(finding)
            
            # Extract suggestion from fix if available
            suggestion = None
            fix_info = finding.get('extra', {}).get('fix')
            if fix_info:
                suggestion = f"Fix: {fix_info}"
            
            return Issue(
                tool="semgrep",
                type=check_id,
                message=message,
                severity=severity,
                file=normalized_path,
                line=start_line,
                rule_id=check_id,
                suggestion=suggestion
            )
            
        except Exception as e:
            self.logger.warning(f"Error converting Semgrep finding: {e}")
            return None
    
    def _determine_semgrep_severity(self, finding: Dict[str, Any]) -> Severity:
        """Determine severity from Semgrep finding."""
        # Try to get severity from metadata
        extra = finding.get('extra', {})
        
        # Check for explicit severity
        if 'severity' in extra:
            raw_severity = extra['severity']
            return self._parse_severity(str(raw_severity))
        
        # Check metadata for severity indicators
        metadata = extra.get('metadata', {})
        if 'severity' in metadata:
            raw_severity = metadata['severity']
            return self._parse_severity(str(raw_severity))
        
        # Infer from rule ID patterns
        check_id = finding.get('check_id', '').lower()
        
        # High severity patterns
        if any(pattern in check_id for pattern in [
            'sql-injection', 'xss', 'command-injection', 'path-traversal',
            'deserialization', 'crypto', 'hardcoded-password', 'rce'
        ]):
            return Severity.HIGH
        
        # Critical patterns
        if any(pattern in check_id for pattern in [
            'critical', 'remote-code-execution', 'authentication-bypass'
        ]):
            return Severity.CRITICAL
        
        # Low severity patterns  
        if any(pattern in check_id for pattern in [
            'info', 'debug', 'comment', 'todo', 'unused'
        ]):
            return Severity.LOW
        
        # Default to medium
        return Severity.MEDIUM


# Register the analyzer
analyzer_registry.register(SemgrepAnalyzer)