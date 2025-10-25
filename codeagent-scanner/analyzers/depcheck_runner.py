"""Dependency checker analyzer for known vulnerabilities in dependencies."""

import json
import os
import subprocess
import tempfile
import time
from typing import List, Dict, Any, Optional
import glob

from .base import BaseAnalyzer, AnalyzerResult, Issue, Severity, analyzer_registry


class DepCheckAnalyzer(BaseAnalyzer):
    """Dependency vulnerability checker using pip-audit and other tools."""
    
    def __init__(self, timeout_sec: int = 300):
        super().__init__(timeout_sec)
        
    @property
    def name(self) -> str:
        return "depcheck"
    
    @property
    def version(self) -> str:
        """Get pip-audit version."""
        try:
            result = subprocess.run(
                ["pip-audit", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # Parse version from output like "pip-audit 2.6.1"
                version_line = result.stdout.strip().split('\n')[0]
                if 'pip-audit' in version_line:
                    return version_line.split('pip-audit')[1].strip()
                return version_line
            return "unknown"
        except Exception:
            return "unknown"
    
    def is_applicable(self, workspace_path: str) -> bool:
        """Check if dependency checking should run on this workspace."""
        # Look for dependency files
        dep_files = self._find_dependency_files(workspace_path)
        return len(dep_files) > 0
    
    def run_analysis(self, workspace_path: str, **kwargs) -> AnalyzerResult:
        """Run dependency vulnerability analysis."""
        start_time = time.time()
        issues = []
        error_message = None
        
        try:
            # Find all dependency files
            dep_files = self._find_dependency_files(workspace_path)
            
            if not dep_files:
                self.logger.info("No dependency files found, skipping dependency check")
                success = True
            else:
                self.logger.info(f"Found dependency files: {dep_files}")
                
                # Run analysis on each type of dependency file
                for dep_file in dep_files:
                    try:
                        file_issues = self._analyze_dependency_file(dep_file, workspace_path)
                        issues.extend(file_issues)
                    except Exception as e:
                        self.logger.warning(f"Failed to analyze {dep_file}: {e}")
                
                success = True
            
        except Exception as e:
            error_message = f"Dependency check failed: {str(e)}"
            success = False
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        return AnalyzerResult(
            tool_name=self.name,
            success=success,
            issues=issues,
            duration_ms=duration_ms,
            error_message=error_message
        )
    
    def _find_dependency_files(self, workspace_path: str) -> List[str]:
        """Find dependency management files in the workspace."""
        dep_patterns = [
            # Python
            'requirements.txt', 'requirements-*.txt', 'Pipfile', 'pyproject.toml',
            # JavaScript/Node  
            'package.json',
            # Java
            'pom.xml', 'build.gradle', 'build.gradle.kts',
            # .NET
            '*.csproj', '*.fsproj', '*.vbproj', 'packages.config',
            # Go
            'go.mod',
            # Ruby
            'Gemfile',
            # PHP
            'composer.json',
            # Rust
            'Cargo.toml'
        ]
        
        found_files = []
        
        for pattern in dep_patterns:
            if '*' in pattern:
                # Use glob for wildcard patterns
                matches = glob.glob(os.path.join(workspace_path, '**', pattern), recursive=True)
                for match in matches:
                    rel_path = os.path.relpath(match, workspace_path)
                    found_files.append(rel_path)
            else:
                # Check if file exists
                file_path = os.path.join(workspace_path, pattern)
                if os.path.exists(file_path):
                    found_files.append(pattern)
        
        return found_files
    
    def _analyze_dependency_file(self, dep_file_path: str, workspace_path: str) -> List[Issue]:
        """Analyze a specific dependency file for vulnerabilities."""
        full_path = os.path.join(workspace_path, dep_file_path)
        file_name = os.path.basename(dep_file_path)
        
        if file_name.startswith('requirements') and file_name.endswith('.txt'):
            return self._analyze_python_requirements(full_path, dep_file_path, workspace_path)
        elif file_name == 'package.json':
            return self._analyze_npm_package(full_path, dep_file_path, workspace_path)
        elif file_name in ['pom.xml', 'build.gradle', 'build.gradle.kts']:
            return self._analyze_java_dependencies(full_path, dep_file_path, workspace_path)
        elif file_name == 'Gemfile':
            return self._analyze_ruby_gems(full_path, dep_file_path, workspace_path)
        else:
            self.logger.debug(f"No specific analyzer for {file_name}")
            return []
    
    def _analyze_python_requirements(self, file_path: str, rel_path: str, workspace_path: str) -> List[Issue]:
        """Analyze Python requirements file using pip-audit."""
        issues = []
        
        try:
            # Create temporary file for output
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as tmp_file:
                output_file = tmp_file.name
            
            # Run pip-audit
            cmd = [
                "pip-audit",
                "--requirement", file_path,
                "--format=json",
                f"--output={output_file}",
                "--no-deps"  # Only check explicit requirements
            ]
            
            self.logger.info(f"Running pip-audit on {rel_path}")
            result = self._run_command(cmd, workspace_path, capture_output=True)
            
            # Parse results
            if os.path.exists(output_file):
                issues = self._parse_pip_audit_output(output_file, rel_path, workspace_path)
                os.unlink(output_file)
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"pip-audit timed out for {rel_path}")
        except Exception as e:
            self.logger.error(f"pip-audit failed for {rel_path}: {e}")
        finally:
            if 'output_file' in locals() and os.path.exists(output_file):
                try:
                    os.unlink(output_file)
                except Exception:
                    pass
        
        return issues
    
    def _analyze_npm_package(self, file_path: str, rel_path: str, workspace_path: str) -> List[Issue]:
        """Analyze npm package.json using npm audit."""
        issues = []
        
        try:
            # Check if package-lock.json or node_modules exists
            pkg_dir = os.path.dirname(file_path)
            
            cmd = ["npm", "audit", "--json", "--audit-level=info"]
            
            self.logger.info(f"Running npm audit on {rel_path}")
            result = self._run_command(cmd, pkg_dir, capture_output=True)
            
            if result.stdout:
                issues = self._parse_npm_audit_output(result.stdout, rel_path, workspace_path)
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"npm audit timed out for {rel_path}")
        except Exception as e:
            self.logger.error(f"npm audit failed for {rel_path}: {e}")
        
        return issues
    
    def _analyze_java_dependencies(self, file_path: str, rel_path: str, workspace_path: str) -> List[Issue]:
        """Analyze Java dependencies (placeholder - would need OWASP Dependency Check)."""
        # This would require OWASP Dependency Check tool
        # For now, return empty list
        self.logger.info(f"Java dependency analysis not yet implemented for {rel_path}")
        return []
    
    def _analyze_ruby_gems(self, file_path: str, rel_path: str, workspace_path: str) -> List[Issue]:
        """Analyze Ruby Gemfile using bundler-audit."""
        issues = []
        
        try:
            gem_dir = os.path.dirname(file_path)
            cmd = ["bundle", "audit", "--format=json"]
            
            self.logger.info(f"Running bundler-audit on {rel_path}")
            result = self._run_command(cmd, gem_dir, capture_output=True)
            
            if result.stdout:
                issues = self._parse_bundler_audit_output(result.stdout, rel_path, workspace_path)
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"bundler-audit timed out for {rel_path}")
        except Exception as e:
            self.logger.error(f"bundler-audit failed for {rel_path}: {e}")
        
        return issues
    
    def _parse_pip_audit_output(self, output_file: str, dep_file: str, workspace_path: str) -> List[Issue]:
        """Parse pip-audit JSON output."""
        issues = []
        
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            vulnerabilities = data.get('vulnerabilities', [])
            
            for vuln in vulnerabilities:
                try:
                    package = vuln.get('package', 'unknown')
                    version = vuln.get('installed_version', 'unknown')
                    vuln_id = vuln.get('id', 'unknown')
                    description = vuln.get('description', 'Vulnerable dependency detected')
                    
                    # Determine severity from CVSS or description
                    severity = self._determine_vulnerability_severity(vuln)
                    
                    # Create suggestion
                    fix_versions = vuln.get('fix_versions', [])
                    suggestion = None
                    if fix_versions:
                        suggestion = f"Upgrade {package} to version {fix_versions[0]} or later"
                    
                    issue = Issue(
                        tool="depcheck",
                        type=vuln_id,
                        message=f"Vulnerable dependency: {package} {version} - {description}",
                        severity=severity,
                        file=dep_file,
                        line=1,  # Dependencies don't have specific line numbers
                        rule_id=vuln_id,
                        suggestion=suggestion
                    )
                    
                    issues.append(issue)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to parse vulnerability: {e}")
        
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse pip-audit JSON: {e}")
        except Exception as e:
            self.logger.error(f"Error reading pip-audit output: {e}")
        
        return issues
    
    def _parse_npm_audit_output(self, json_output: str, dep_file: str, workspace_path: str) -> List[Issue]:
        """Parse npm audit JSON output."""
        issues = []
        
        try:
            data = json.loads(json_output)
            vulnerabilities = data.get('vulnerabilities', {})
            
            for package_name, vuln_info in vulnerabilities.items():
                try:
                    severity_raw = vuln_info.get('severity', 'moderate')
                    severity = self._parse_severity(severity_raw)
                    
                    # Get vulnerability details
                    via = vuln_info.get('via', [])
                    if isinstance(via, list) and via:
                        vuln_detail = via[0] if isinstance(via[0], dict) else {}
                        title = vuln_detail.get('title', 'Vulnerable dependency')
                        vuln_id = vuln_detail.get('cwe', ['unknown'])[0] if vuln_detail.get('cwe') else 'unknown'
                    else:
                        title = f"Vulnerable dependency: {package_name}"
                        vuln_id = 'npm-audit'
                    
                    issue = Issue(
                        tool="depcheck",
                        type=vuln_id,
                        message=title,
                        severity=severity,
                        file=dep_file,
                        line=1,
                        rule_id=vuln_id,
                        suggestion=f"Update {package_name} to a secure version"
                    )
                    
                    issues.append(issue)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to parse npm vulnerability for {package_name}: {e}")
        
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse npm audit JSON: {e}")
        except Exception as e:
            self.logger.error(f"Error parsing npm audit output: {e}")
        
        return issues
    
    def _parse_bundler_audit_output(self, json_output: str, dep_file: str, workspace_path: str) -> List[Issue]:
        """Parse bundler-audit JSON output."""
        # Implementation for Ruby bundler-audit would go here
        return []
    
    def _determine_vulnerability_severity(self, vuln: Dict[str, Any]) -> Severity:
        """Determine severity from vulnerability data."""
        # Try to get CVSS score
        cvss_score = None
        
        # pip-audit format
        if 'aliases' in vuln:
            for alias in vuln['aliases']:
                if alias.startswith('GHSA-'):
                    # GitHub Security Advisory - typically high severity
                    return Severity.HIGH
        
        # Look for CVE severity indicators
        vuln_id = vuln.get('id', '').upper()
        description = vuln.get('description', '').lower()
        
        # Critical indicators
        if any(term in description for term in [
            'remote code execution', 'rce', 'critical', 'arbitrary code'
        ]):
            return Severity.CRITICAL
        
        # High severity indicators
        if any(term in description for term in [
            'code injection', 'sql injection', 'xss', 'csrf', 'authentication bypass'
        ]):
            return Severity.HIGH
        
        # Default based on vulnerability type
        if vuln_id.startswith('CVE-'):
            return Severity.HIGH
        
        return Severity.MEDIUM


# Register the analyzer
analyzer_registry.register(DepCheckAnalyzer)