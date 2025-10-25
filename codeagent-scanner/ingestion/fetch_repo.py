"""Repository fetching and extraction functionality."""

import os
import shutil
import subprocess
import tempfile
import zipfile
import logging
from typing import Optional, Dict, Any
from urllib.parse import urlparse
import uuid


logger = logging.getLogger(__name__)


class RepoFetchError(Exception):
    """Exception raised when repository fetching fails."""
    pass


class RepoFetcher:
    """Handles fetching and extracting repositories from various sources."""
    
    def __init__(self, storage_base: str, allowed_hosts: Optional[list] = None):
        """
        Initialize RepoFetcher.
        
        Args:
            storage_base: Base directory for storing workspaces
            allowed_hosts: List of allowed hosts for GitHub URLs (e.g., ['github.com'])
        """
        self.storage_base = storage_base
        self.allowed_hosts = allowed_hosts or ['github.com']
        
    def fetch_github_repo(
        self, 
        github_url: str, 
        job_id: str,
        ref: Optional[str] = None,
        commit: Optional[str] = None,
        timeout_sec: int = 300
    ) -> str:
        """
        Clone a GitHub repository.
        
        Args:
            github_url: GitHub repository URL
            job_id: Unique job identifier
            ref: Branch or tag to checkout (optional)
            commit: Specific commit SHA to checkout (optional)
            timeout_sec: Timeout for git operations
            
        Returns:
            Path to the cloned workspace
            
        Raises:
            RepoFetchError: If cloning fails
        """
        # Validate URL
        self._validate_github_url(github_url)
        
        # Create workspace directory
        workspace_path = os.path.join(self.storage_base, "workspace", job_id)
        os.makedirs(workspace_path, exist_ok=True)
        
        try:
            logger.info(f"Cloning {github_url} to {workspace_path}")
            
            # Build git clone command
            clone_cmd = [
                "git", "clone",
                "--depth", "1",  # Shallow clone for speed
                "--quiet"
            ]
            
            # Add branch/tag if specified
            if ref:
                clone_cmd.extend(["-b", ref])
            
            clone_cmd.extend([github_url, workspace_path])
            
            # Execute git clone
            result = subprocess.run(
                clone_cmd,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                check=False
            )
            
            if result.returncode != 0:
                raise RepoFetchError(f"Git clone failed: {result.stderr}")
            
            # Checkout specific commit if provided
            if commit:
                logger.info(f"Checking out commit {commit}")
                self._checkout_commit(workspace_path, commit, timeout_sec)
            
            # Remove .git directory to save space and avoid confusion
            git_dir = os.path.join(workspace_path, '.git')
            if os.path.exists(git_dir):
                shutil.rmtree(git_dir)
            
            logger.info(f"Successfully cloned repository to {workspace_path}")
            return workspace_path
            
        except subprocess.TimeoutExpired:
            self._cleanup_workspace(workspace_path)
            raise RepoFetchError(f"Git clone timed out after {timeout_sec} seconds")
        except Exception as e:
            self._cleanup_workspace(workspace_path)
            raise RepoFetchError(f"Failed to clone repository: {str(e)}")
    
    def extract_zip_archive(self, zip_file_path: str, job_id: str) -> str:
        """
        Extract a ZIP archive to a workspace.
        
        Args:
            zip_file_path: Path to the ZIP file
            job_id: Unique job identifier
            
        Returns:
            Path to the extracted workspace
            
        Raises:
            RepoFetchError: If extraction fails
        """
        # Create workspace directory
        workspace_path = os.path.join(self.storage_base, "workspace", job_id)
        os.makedirs(workspace_path, exist_ok=True)
        
        try:
            logger.info(f"Extracting ZIP archive {zip_file_path} to {workspace_path}")
            
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                # Security check: prevent path traversal
                for member in zip_ref.namelist():
                    if os.path.isabs(member) or ".." in member:
                        raise RepoFetchError(f"Unsafe ZIP entry: {member}")
                
                # Extract all files
                zip_ref.extractall(workspace_path)
            
            # If extracted to a single top-level directory, flatten it
            extracted_items = os.listdir(workspace_path)
            if len(extracted_items) == 1 and os.path.isdir(os.path.join(workspace_path, extracted_items[0])):
                # Move contents up one level
                top_dir = os.path.join(workspace_path, extracted_items[0])
                temp_dir = os.path.join(workspace_path, f"_temp_{uuid.uuid4().hex[:8]}")
                shutil.move(top_dir, temp_dir)
                
                for item in os.listdir(temp_dir):
                    shutil.move(os.path.join(temp_dir, item), os.path.join(workspace_path, item))
                
                os.rmdir(temp_dir)
            
            logger.info(f"Successfully extracted ZIP archive to {workspace_path}")
            return workspace_path
            
        except zipfile.BadZipFile:
            self._cleanup_workspace(workspace_path)
            raise RepoFetchError("Invalid ZIP file format")
        except Exception as e:
            self._cleanup_workspace(workspace_path)
            raise RepoFetchError(f"Failed to extract ZIP archive: {str(e)}")
    
    def _validate_github_url(self, url: str) -> None:
        """
        Validate that the GitHub URL is allowed.
        
        Args:
            url: GitHub repository URL
            
        Raises:
            RepoFetchError: If URL is invalid or not allowed
        """
        try:
            parsed = urlparse(url)
        except Exception:
            raise RepoFetchError("Invalid URL format")
        
        # Check scheme
        if parsed.scheme not in ['http', 'https']:
            raise RepoFetchError("Only HTTP/HTTPS URLs are allowed")
        
        # Check host against allowed list
        if parsed.hostname not in self.allowed_hosts:
            raise RepoFetchError(f"Host {parsed.hostname} is not in the allowed list: {self.allowed_hosts}")
        
        # Basic GitHub URL format check
        if parsed.hostname == 'github.com':
            path_parts = parsed.path.strip('/').split('/')
            if len(path_parts) < 2:
                raise RepoFetchError("Invalid GitHub repository URL format")
    
    def _checkout_commit(self, workspace_path: str, commit: str, timeout_sec: int) -> None:
        """
        Checkout a specific commit in the cloned repository.
        
        Args:
            workspace_path: Path to the Git repository
            commit: Commit SHA to checkout
            timeout_sec: Timeout for git operations
            
        Raises:
            RepoFetchError: If checkout fails
        """
        try:
            # First, fetch the commit (in case it's not in shallow clone)
            fetch_cmd = ["git", "fetch", "origin", commit]
            result = subprocess.run(
                fetch_cmd,
                cwd=workspace_path,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                check=False
            )
            
            # Checkout the commit
            checkout_cmd = ["git", "checkout", commit]
            result = subprocess.run(
                checkout_cmd,
                cwd=workspace_path,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                check=False
            )
            
            if result.returncode != 0:
                raise RepoFetchError(f"Git checkout failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise RepoFetchError(f"Git checkout timed out after {timeout_sec} seconds")
        except Exception as e:
            raise RepoFetchError(f"Failed to checkout commit {commit}: {str(e)}")
    
    def _cleanup_workspace(self, workspace_path: str) -> None:
        """Clean up a workspace directory on error."""
        try:
            if os.path.exists(workspace_path):
                shutil.rmtree(workspace_path)
                logger.info(f"Cleaned up workspace: {workspace_path}")
        except Exception as e:
            logger.error(f"Failed to cleanup workspace {workspace_path}: {e}")
    
    def cleanup_workspace(self, job_id: str) -> None:
        """
        Public method to clean up workspace for a job.
        
        Args:
            job_id: Job identifier
        """
        workspace_path = os.path.join(self.storage_base, "workspace", job_id)
        self._cleanup_workspace(workspace_path)
    
    def get_workspace_path(self, job_id: str) -> str:
        """
        Get workspace path for a job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Path to the workspace directory
        """
        return os.path.join(self.storage_base, "workspace", job_id)
    
    def workspace_exists(self, job_id: str) -> bool:
        """
        Check if workspace exists for a job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if workspace exists
        """
        workspace_path = self.get_workspace_path(job_id)
        return os.path.exists(workspace_path) and os.path.isdir(workspace_path)