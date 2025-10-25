"""Workspace sanitization and filtering functionality."""

import os
import shutil
import glob
import fnmatch
import logging
from typing import List, Set, Optional
import stat


logger = logging.getLogger(__name__)


class WorkspaceSanitizer:
    """Sanitizes workspaces by removing unwanted files and directories."""
    
    def __init__(self):
        # Default ignore patterns
        self.ignore_dirs = {
            # Version control
            '.git', '.svn', '.hg', '.bzr',
            # Dependencies/build artifacts
            'node_modules', 'bower_components', 'vendor',
            '__pycache__', '.pytest_cache', 'venv', '.venv', 'env', '.env',
            'target', 'build', 'dist', 'out', 'bin', 'obj',
            # IDE/editor files
            '.idea', '.vscode', '.vs', '.eclipse',
            # Cache/temp
            'tmp', 'temp', 'cache', '.cache', '.tmp',
            # Logs
            'logs', 'log',
            # OS specific
            '.DS_Store', 'Thumbs.db'
        }
        
        self.ignore_files = {
            # Compiled files
            '*.pyc', '*.pyo', '*.pyd', '*.class', '*.jar', '*.war', '*.ear',
            '*.o', '*.so', '*.dll', '*.dylib', '*.a', '*.lib',
            # Executables
            '*.exe', '*.bin', '*.app',
            # Archives
            '*.zip', '*.tar', '*.gz', '*.bz2', '*.xz', '*.rar', '*.7z',
            # Media files
            '*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.svg', '*.ico',
            '*.mp3', '*.mp4', '*.avi', '*.mov', '*.wmv', '*.flv',
            # Documents
            '*.pdf', '*.doc', '*.docx', '*.xls', '*.xlsx', '*.ppt', '*.pptx',
            # Temp/backup files
            '*.tmp', '*.temp', '*.bak', '*.backup', '*~', '*.swp', '*.swo',
            # OS specific
            '.DS_Store', 'Thumbs.db', 'desktop.ini'
        }
        
        # File size limit (20MB)
        self.max_file_size = 20 * 1024 * 1024
        
    def sanitize_workspace(
        self,
        workspace_path: str,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        max_files: int = 10000
    ) -> dict:
        """
        Sanitize a workspace by removing unwanted files and applying filters.
        
        Args:
            workspace_path: Path to the workspace
            include_patterns: List of glob patterns to include (e.g., ['src/**/*.py'])
            exclude_patterns: List of glob patterns to exclude (e.g., ['tests/**'])
            max_files: Maximum number of files to keep
            
        Returns:
            Dictionary with sanitization statistics
        """
        if not os.path.exists(workspace_path):
            raise ValueError(f"Workspace path does not exist: {workspace_path}")
        
        stats = {
            'files_before': 0,
            'files_after': 0,
            'dirs_removed': 0,
            'files_removed': 0,
            'size_reduced_mb': 0
        }
        
        logger.info(f"Sanitizing workspace: {workspace_path}")
        
        # Count initial files
        stats['files_before'] = self._count_files(workspace_path)
        initial_size = self._get_directory_size(workspace_path)
        
        # Remove ignored directories first
        stats['dirs_removed'] = self._remove_ignored_directories(workspace_path)
        
        # Remove ignored files
        stats['files_removed'] = self._remove_ignored_files(workspace_path)
        
        # Apply include/exclude filters
        if include_patterns or exclude_patterns:
            filtered = self._apply_filters(workspace_path, include_patterns, exclude_patterns)
            stats['files_removed'] += filtered
        
        # Enforce file count limit
        if max_files > 0:
            limited = self._enforce_file_limit(workspace_path, max_files)
            stats['files_removed'] += limited
        
        # Count final files and size
        stats['files_after'] = self._count_files(workspace_path)
        final_size = self._get_directory_size(workspace_path)
        stats['size_reduced_mb'] = round((initial_size - final_size) / (1024 * 1024), 2)
        
        logger.info(f"Workspace sanitization complete: {stats}")
        return stats
    
    def _remove_ignored_directories(self, workspace_path: str) -> int:
        """Remove ignored directories from workspace."""
        removed_count = 0
        
        for root, dirs, files in os.walk(workspace_path, topdown=True):
            # Filter out ignored directories (modifying dirs in-place affects os.walk)
            dirs_to_remove = []
            for dir_name in dirs:
                if self._should_ignore_directory(dir_name):
                    dir_path = os.path.join(root, dir_name)
                    logger.debug(f"Removing ignored directory: {dir_path}")
                    try:
                        shutil.rmtree(dir_path)
                        dirs_to_remove.append(dir_name)
                        removed_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to remove directory {dir_path}: {e}")
            
            # Remove from dirs list so os.walk doesn't traverse them
            for dir_name in dirs_to_remove:
                dirs.remove(dir_name)
        
        return removed_count
    
    def _remove_ignored_files(self, workspace_path: str) -> int:
        """Remove ignored files from workspace."""
        removed_count = 0
        
        for root, dirs, files in os.walk(workspace_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                
                if self._should_ignore_file(file_name, file_path):
                    logger.debug(f"Removing ignored file: {file_path}")
                    try:
                        os.remove(file_path)
                        removed_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to remove file {file_path}: {e}")
        
        return removed_count
    
    def _apply_filters(
        self,
        workspace_path: str,
        include_patterns: Optional[List[str]],
        exclude_patterns: Optional[List[str]]
    ) -> int:
        """Apply include/exclude pattern filters."""
        if not include_patterns and not exclude_patterns:
            return 0
        
        removed_count = 0
        
        # Get all files
        all_files = []
        for root, dirs, files in os.walk(workspace_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                rel_path = os.path.relpath(file_path, workspace_path)
                all_files.append((file_path, rel_path))
        
        # Apply filters
        for file_path, rel_path in all_files:
            should_keep = True
            
            # Check include patterns (if specified, file must match at least one)
            if include_patterns:
                should_keep = any(fnmatch.fnmatch(rel_path, pattern) for pattern in include_patterns)
            
            # Check exclude patterns (if file matches any, exclude it)
            if exclude_patterns and should_keep:
                should_keep = not any(fnmatch.fnmatch(rel_path, pattern) for pattern in exclude_patterns)
            
            # Remove file if it doesn't match criteria
            if not should_keep:
                logger.debug(f"Filtering out file: {rel_path}")
                try:
                    os.remove(file_path)
                    removed_count += 1
                except Exception as e:
                    logger.warning(f"Failed to remove filtered file {file_path}: {e}")
        
        return removed_count
    
    def _enforce_file_limit(self, workspace_path: str, max_files: int) -> int:
        """Enforce maximum number of files limit."""
        # Get all files with their sizes
        all_files = []
        for root, dirs, files in os.walk(workspace_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                try:
                    file_size = os.path.getsize(file_path)
                    all_files.append((file_path, file_size))
                except Exception as e:
                    logger.warning(f"Could not get size for {file_path}: {e}")
        
        if len(all_files) <= max_files:
            return 0
        
        # Sort by size (keep smaller files)
        all_files.sort(key=lambda x: x[1])
        
        # Remove largest files
        files_to_remove = all_files[max_files:]
        removed_count = 0
        
        for file_path, _ in files_to_remove:
            logger.debug(f"Removing file due to limit: {file_path}")
            try:
                os.remove(file_path)
                removed_count += 1
            except Exception as e:
                logger.warning(f"Failed to remove file {file_path}: {e}")
        
        logger.info(f"Enforced file limit: removed {removed_count} files, kept {max_files}")
        return removed_count
    
    def _should_ignore_directory(self, dir_name: str) -> bool:
        """Check if directory should be ignored."""
        return dir_name.lower() in self.ignore_dirs or dir_name.startswith('.')
    
    def _should_ignore_file(self, file_name: str, file_path: str) -> bool:
        """Check if file should be ignored."""
        # Check against ignore patterns
        for pattern in self.ignore_files:
            if fnmatch.fnmatch(file_name.lower(), pattern.lower()):
                return True
        
        # Check file size
        try:
            if os.path.getsize(file_path) > self.max_file_size:
                logger.debug(f"File too large: {file_path}")
                return True
        except Exception:
            return True  # If we can't get size, probably ignore it
        
        # Check if file is hidden (starts with .)
        if file_name.startswith('.') and file_name not in ['.gitignore', '.dockerignore', '.env.example']:
            return True
        
        return False
    
    def _count_files(self, directory: str) -> int:
        """Count total number of files in directory."""
        count = 0
        try:
            for root, dirs, files in os.walk(directory):
                count += len(files)
        except Exception as e:
            logger.warning(f"Error counting files in {directory}: {e}")
        return count
    
    def _get_directory_size(self, directory: str) -> int:
        """Get total size of directory in bytes."""
        total_size = 0
        try:
            for root, dirs, files in os.walk(directory):
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    try:
                        total_size += os.path.getsize(file_path)
                    except Exception:
                        continue
        except Exception as e:
            logger.warning(f"Error calculating directory size for {directory}: {e}")
        return total_size
    
    def add_ignore_pattern(self, pattern: str, is_directory: bool = False) -> None:
        """Add a custom ignore pattern."""
        if is_directory:
            self.ignore_dirs.add(pattern)
        else:
            self.ignore_files.add(pattern)
        logger.debug(f"Added ignore pattern: {pattern} (directory: {is_directory})")
    
    def remove_ignore_pattern(self, pattern: str, is_directory: bool = False) -> None:
        """Remove an ignore pattern."""
        if is_directory:
            self.ignore_dirs.discard(pattern)
        else:
            self.ignore_files.discard(pattern)
        logger.debug(f"Removed ignore pattern: {pattern} (directory: {is_directory})")
    
    def get_workspace_info(self, workspace_path: str) -> dict:
        """Get information about a workspace."""
        if not os.path.exists(workspace_path):
            return {"error": "Workspace does not exist"}
        
        info = {
            'path': workspace_path,
            'exists': True,
            'total_files': 0,
            'total_size_mb': 0,
            'file_types': {},
            'languages_detected': set()
        }
        
        try:
            total_size = 0
            file_extensions = {}
            
            for root, dirs, files in os.walk(workspace_path):
                info['total_files'] += len(files)
                
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    
                    # Count file size
                    try:
                        file_size = os.path.getsize(file_path)
                        total_size += file_size
                    except Exception:
                        continue
                    
                    # Count file extensions
                    _, ext = os.path.splitext(file_name)
                    if ext:
                        ext = ext.lower()
                        file_extensions[ext] = file_extensions.get(ext, 0) + 1
                        
                        # Detect programming languages
                        lang = self._detect_language_from_extension(ext)
                        if lang:
                            info['languages_detected'].add(lang)
            
            info['total_size_mb'] = round(total_size / (1024 * 1024), 2)
            info['file_types'] = file_extensions
            info['languages_detected'] = list(info['languages_detected'])
            
        except Exception as e:
            logger.error(f"Error getting workspace info: {e}")
            info['error'] = str(e)
        
        return info
    
    def _detect_language_from_extension(self, ext: str) -> Optional[str]:
        """Detect programming language from file extension."""
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.go': 'Go',
            '.c': 'C',
            '.cpp': 'C++',
            '.cc': 'C++',
            '.cxx': 'C++',
            '.h': 'C/C++',
            '.hpp': 'C++',
            '.cs': 'C#',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.rs': 'Rust',
            '.sh': 'Shell',
            '.bash': 'Bash',
        }
        return language_map.get(ext.lower())