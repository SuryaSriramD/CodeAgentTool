"""Analyzer detection and selection logic."""

import os
import glob
from typing import List, Set
import logging


logger = logging.getLogger(__name__)


def detect_applicable_analyzers(workspace_path: str, available_analyzers: List[str]) -> List[str]:
    """
    Detect which analyzers should run based on workspace contents.
    
    Args:
        workspace_path: Path to the workspace to analyze
        available_analyzers: List of available analyzer names
        
    Returns:
        List of analyzer names that should be applied
    """
    applicable = []
    
    # Get file extensions and special files in workspace
    file_info = _scan_workspace(workspace_path)
    
    for analyzer in available_analyzers:
        if _is_analyzer_applicable(analyzer, file_info, workspace_path):
            applicable.append(analyzer)
            logger.info(f"Analyzer '{analyzer}' is applicable for workspace")
        else:
            logger.debug(f"Analyzer '{analyzer}' not applicable for workspace")
    
    return applicable


def _scan_workspace(workspace_path: str) -> dict:
    """
    Scan workspace to get file type information.
    
    Returns:
        Dict with file extensions, special files, and other metadata
    """
    file_info = {
        'extensions': set(),
        'files': set(),
        'total_files': 0,
        'directories': set()
    }
    
    try:
        for root, dirs, files in os.walk(workspace_path):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if not _is_ignored_directory(d)]
            
            for file in files:
                if _is_ignored_file(file):
                    continue
                    
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, workspace_path)
                
                file_info['files'].add(rel_path)
                file_info['total_files'] += 1
                
                # Get file extension
                _, ext = os.path.splitext(file)
                if ext:
                    file_info['extensions'].add(ext.lower())
            
            # Track directories
            for dir_name in dirs:
                dir_path = os.path.relpath(os.path.join(root, dir_name), workspace_path)
                file_info['directories'].add(dir_path)
    
    except Exception as e:
        logger.error(f"Error scanning workspace {workspace_path}: {e}")
    
    return file_info


def _is_analyzer_applicable(analyzer_name: str, file_info: dict, workspace_path: str) -> bool:
    """
    Check if a specific analyzer should run based on workspace contents.
    
    Args:
        analyzer_name: Name of the analyzer
        file_info: File information from _scan_workspace
        workspace_path: Path to workspace
        
    Returns:
        True if analyzer should run
    """
    
    if analyzer_name == "bandit":
        # Bandit for Python files
        python_exts = {'.py', '.pyw'}
        return bool(file_info['extensions'] & python_exts)
    
    elif analyzer_name == "semgrep":
        # Semgrep supports multiple languages - run if any supported files
        supported_exts = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', 
            '.c', '.cpp', '.cc', '.cxx', '.h', '.hpp',
            '.rb', '.php', '.scala', '.kt', '.swift',
            '.cs', '.fs', '.vb', '.rs', '.sh', '.bash',
            '.yaml', '.yml', '.json', '.xml', '.html',
            '.dockerfile'
        }
        return bool(file_info['extensions'] & supported_exts)
    
    elif analyzer_name == "depcheck" or analyzer_name == "dep":
        # Dependency check - look for dependency files
        dep_files = _find_dependency_files(workspace_path, file_info)
        return len(dep_files) > 0
    
    elif analyzer_name == "eslint":
        # ESLint for JavaScript/TypeScript
        js_exts = {'.js', '.jsx', '.ts', '.tsx', '.vue'}
        return bool(file_info['extensions'] & js_exts)
    
    elif analyzer_name == "gosec":
        # GoSec for Go files
        return '.go' in file_info['extensions']
    
    elif analyzer_name == "safety":
        # Safety for Python dependencies
        python_exts = {'.py', '.pyw'}
        has_python = bool(file_info['extensions'] & python_exts)
        has_requirements = any(f for f in file_info['files'] if f.endswith('requirements.txt'))
        return has_python or has_requirements
    
    # Default: run analyzer if we don't know better
    return True


def _find_dependency_files(workspace_path: str, file_info: dict) -> List[str]:
    """
    Find dependency management files in the workspace.
    
    Returns:
        List of dependency files found
    """
    dep_patterns = [
        # Python
        'requirements.txt', 'requirements-*.txt', 'Pipfile', 'pyproject.toml', 'setup.py',
        # JavaScript/Node
        'package.json', 'package-lock.json', 'yarn.lock', 'npm-shrinkwrap.json',
        # Java
        'pom.xml', 'build.gradle', 'build.gradle.kts', 'gradle.properties',
        # .NET
        '*.csproj', '*.fsproj', '*.vbproj', 'packages.config', '*.sln',
        # Go
        'go.mod', 'go.sum', 'Gopkg.toml', 'Gopkg.lock',
        # Ruby
        'Gemfile', 'Gemfile.lock', '*.gemspec',
        # PHP
        'composer.json', 'composer.lock',
        # Rust
        'Cargo.toml', 'Cargo.lock',
    ]
    
    found_files = []
    
    for pattern in dep_patterns:
        if '*' in pattern:
            # Use glob for wildcard patterns
            matches = glob.glob(os.path.join(workspace_path, '**', pattern), recursive=True)
            for match in matches:
                rel_path = os.path.relpath(match, workspace_path)
                if not _is_ignored_file(os.path.basename(match)):
                    found_files.append(rel_path)
        else:
            # Direct file check
            if pattern in [os.path.basename(f) for f in file_info['files']]:
                found_files.append(pattern)
    
    return found_files


def _is_ignored_directory(dir_name: str) -> bool:
    """Check if directory should be ignored."""
    ignored_dirs = {
        '.git', '.svn', '.hg', '.bzr',  # VCS
        'node_modules', 'bower_components',  # JS
        '__pycache__', '.pytest_cache', 'venv', '.venv', 'env', '.env',  # Python
        'target', 'build', 'dist', 'out',  # Build outputs
        '.idea', '.vscode', '.vs',  # IDEs
        'vendor',  # Dependencies
        'tmp', 'temp', 'cache', '.cache',  # Temp
        'logs', 'log',  # Logs
    }
    return dir_name.lower() in ignored_dirs or dir_name.startswith('.')


def _is_ignored_file(file_name: str) -> bool:
    """Check if file should be ignored."""
    # Ignore hidden files, temp files, and large binaries
    if file_name.startswith('.') and file_name not in ['.gitignore', '.dockerignore']:
        return True
    
    # Ignore common non-source files
    ignored_exts = {
        '.pyc', '.pyo', '.pyd',  # Python compiled
        '.class', '.jar',  # Java compiled  
        '.o', '.so', '.dll', '.dylib',  # Compiled binaries
        '.exe', '.bin',  # Executables
        '.zip', '.tar', '.gz', '.bz2', '.xz',  # Archives
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg',  # Images
        '.mp3', '.mp4', '.avi', '.mov', '.wmv',  # Media
        '.pdf', '.doc', '.docx', '.xls', '.xlsx',  # Documents
        '.log', '.tmp', '.temp', '.cache',  # Temp/log files
    }
    
    _, ext = os.path.splitext(file_name)
    return ext.lower() in ignored_exts


def get_analyzer_defaults() -> List[str]:
    """Get default set of analyzers to run."""
    return ["bandit", "semgrep", "depcheck"]


def filter_analyzers_by_config(requested: List[str], allowed: List[str]) -> List[str]:
    """
    Filter requested analyzers by allowed list.
    
    Args:
        requested: List of requested analyzer names
        allowed: List of allowed analyzer names
        
    Returns:
        Filtered list of analyzers
    """
    if not allowed:  # If no restrictions, allow all
        return requested
    
    filtered = [analyzer for analyzer in requested if analyzer in allowed]
    
    if len(filtered) != len(requested):
        skipped = set(requested) - set(filtered)
        logger.warning(f"Skipped disallowed analyzers: {skipped}")
    
    return filtered