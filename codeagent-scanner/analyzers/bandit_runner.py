"""Bandit security analyzer runner for Python code."""

import json
import os
import subprocess
import tempfile
import time
from typing import List, Dict, Any, Optional

from .base import BaseAnalyzer, AnalyzerResult, Issue, Severity, analyzer_registry


class BanditAnalyzer(BaseAnalyzer):
    """Bandit static analysis security scanner for Python."""
    
    def __init__(self, timeout_sec: int = 300, confidence_level: str = "low"):
        super().__init__(timeout_sec)
        self.confidence_level = confidence_level  # low, medium, high
        
    @property
    def name(self) -> str:
        return "bandit"
    
    @property 
    def version(self) -> str:
        """Get Bandit version."""
        try:
            result = subprocess.run(
                ["bandit", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # Parse version from output like "bandit 1.7.9"
                version_line = result.stdout.strip().split('\n')[0]
                if 'bandit' in version_line:
                    return version_line.split('bandit')[1].strip()
                return version_line
            return "unknown"
        except Exception:
            return "unknown"
    
    def is_applicable(self, workspace_path: str) -> bool:
        """Check if Bandit should run on this workspace."""
        # Look for Python files
        try:
            for root, dirs, files in os.walk(workspace_path):
                # Skip common ignore directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'venv', '.venv']]
                
                for file in files:
                    if file.endswith(('.py', '.pyw')):
                        return True
            return False
        except Exception as e:
            self.logger.error(f"Error checking workspace applicability: {e}")
            return False
    
    def run_analysis(self, workspace_path: str, **kwargs) -> AnalyzerResult:
        """Run Bandit analysis on Python files in the workspace."""
        start_time = time.time()
        issues = []
        error_message = None
        
        try:
            # Create temporary file for output
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as tmp_file:
                output_file = tmp_file.name
            
            # Build Bandit command
            cmd = [
                "bandit",
                "-r",  # Recursive
                "-f", "json",  # JSON format
                "-o", output_file,  # Output file
                "-ll",  # Low confidence level (catch more issues)
                workspace_path
            ]
            
            # Add confidence level filter
            if self.confidence_level in ["medium", "high"]:
                cmd.extend(["-i", "-I"])  # Include confidence levels
            
            self.logger.info(f"Running Bandit with command: {' '.join(cmd)}")
            
            # Run Bandit
            result = self._run_command(cmd, workspace_path, capture_output=True)
            
            # Parse results
            if os.path.exists(output_file):
                issues = self._parse_bandit_output(output_file, workspace_path)
                os.unlink(output_file)  # Clean up temp file
            
            # Bandit returns 1 when issues are found, which is expected
            success = result.returncode in [0, 1]  # 0 = no issues, 1 = issues found
            
            if result.returncode > 1:
                error_message = f"Bandit failed with code {result.returncode}: {result.stderr}"
                success = False
            
        except subprocess.TimeoutExpired:
            error_message = f"Bandit analysis timed out after {self.timeout_sec} seconds"
            success = False
        except Exception as e:
            error_message = f"Bandit analysis failed: {str(e)}"
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
    
    def _parse_bandit_output(self, output_file: str, workspace_path: str) -> List[Issue]:
        """Parse Bandit JSON output into normalized Issues."""
        issues = []
        
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Bandit JSON format has 'results' array
            results = data.get('results', [])
            
            for finding in results:
                try:
                    issue = self._convert_bandit_finding(finding, workspace_path)
                    if issue:
                        issues.append(issue)
                except Exception as e:
                    self.logger.warning(f"Failed to parse Bandit finding: {e}")
                    continue
        
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse Bandit JSON output: {e}")
        except Exception as e:
            self.logger.error(f"Error reading Bandit output: {e}")
        
        return issues
    
    def _convert_bandit_finding(self, finding: Dict[str, Any], workspace_path: str) -> Optional[Issue]:
        """Convert a single Bandit finding to normalized Issue."""
        try:
            # Extract basic information
            test_id = finding.get('test_id', 'unknown')
            test_name = finding.get('test_name', 'Security Issue')
            issue_text = finding.get('issue_text', 'Security vulnerability detected')
            
            # Get file path and line number
            filename = finding.get('filename', '')
            line_number = finding.get('line_number', 1)
            
            # Normalize file path
            normalized_path = self._normalize_file_path(filename, workspace_path)
            
            # Determine severity
            severity = self._determine_bandit_severity(finding)
            
            # Create suggestion from Bandit's more_info if available
            suggestion = None
            more_info = finding.get('more_info')
            if more_info:
                suggestion = f"See: {more_info}"
            
            return Issue(
                tool="bandit",
                type=test_id,
                message=issue_text,
                severity=severity,
                file=normalized_path,
                line=line_number,
                rule_id=test_id,
                suggestion=suggestion
            )
            
        except Exception as e:
            self.logger.warning(f"Error converting Bandit finding: {e}")
            return None
    
    def _determine_bandit_severity(self, finding: Dict[str, Any]) -> Severity:
        """Determine severity from Bandit finding."""
        # Bandit provides issue_severity
        raw_severity = finding.get('issue_severity', 'MEDIUM')
        
        # Map Bandit severity to our enum
        severity_map = {
            'LOW': Severity.LOW,
            'MEDIUM': Severity.MEDIUM, 
            'HIGH': Severity.HIGH
        }
        
        severity = severity_map.get(raw_severity.upper(), Severity.MEDIUM)
        
        # Check for critical patterns in test IDs
        test_id = finding.get('test_id', '').upper()
        critical_tests = {
            'B102',  # exec_used
            'B103',  # set_bad_file_permissions  
            'B104',  # hardcoded_bind_all_interfaces
            'B105',  # hardcoded_password_string
            'B106',  # hardcoded_password_funcarg
            'B107',  # hardcoded_password_default
            'B108',  # hardcoded_tmp_directory
            'B201',  # flask_debug_true
            'B501',  # request_with_no_cert_validation
            'B502',  # ssl_with_bad_version
            'B503',  # ssl_with_bad_defaults
            'B504',  # ssl_with_no_version
            'B505',  # weak_cryptographic_key
            'B506',  # yaml_load
            'B601',  # paramiko_calls
            'B602',  # subprocess_popen_with_shell_equals_true
            'B603',  # subprocess_without_shell_equals_true
            'B604',  # any_other_function_with_shell_equals_true
            'B605',  # start_process_with_a_shell
            'B606',  # start_process_with_no_shell
            'B607',  # start_process_with_partial_path
            'B608',  # hardcoded_sql_expressions
            'B609',  # linux_commands_wildcard_injection
            'B701',  # jinja2_autoescape_false
            'B702',  # use_of_mako_templates
            'B703'   # django_mark_safe
        }
        
        if test_id in critical_tests and severity == Severity.HIGH:
            return Severity.CRITICAL
        
        return severity


# Register the analyzer
analyzer_registry.register(BanditAnalyzer)