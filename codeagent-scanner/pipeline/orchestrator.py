"""Job orchestration and management system."""

import asyncio
import json
import logging
import os
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Callable, Any
from dataclasses import asdict

from analyzers.base import analyzer_registry
from analyzers.detect import detect_applicable_analyzers, get_analyzer_defaults, filter_analyzers_by_config
from ingestion.fetch_repo import RepoFetcher, RepoFetchError
from ingestion.sanitize import WorkspaceSanitizer
from pipeline.report_schema import (
    JobInfo, JobStatus, JobPhase, JobProgress, Report, ReportBuilder,
    RepoInfo, AnalyzeRequest, SeveritySummary
)


logger = logging.getLogger(__name__)


class JobOrchestrator:
    """Orchestrates security scanning jobs from submission to completion."""
    
    def __init__(self, storage_base: str, max_workers: int = 4):
        self.storage_base = storage_base
        self.max_workers = max_workers
        
        # Job tracking
        self.active_jobs: Dict[str, JobInfo] = {}
        self.job_threads: Dict[str, threading.Thread] = {}
        self.job_lock = threading.Lock()
        
        # Components
        self.repo_fetcher = RepoFetcher(storage_base)
        self.sanitizer = WorkspaceSanitizer()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Configuration
        self.analyzer_config = {
            "defaults": ["bandit", "semgrep", "depcheck"],
            "rulesets": {
                "semgrep": ["p/owasp-top-ten", "p/security-audit"],
                "bandit": []
            },
            "allow_list": ["https://github.com/"]
        }
        
        # Event callbacks
        self.event_callbacks: List[Callable[[str, str, Dict], None]] = []
        
        # Cleanup thread
        self._start_cleanup_thread()
    
    def submit_job(self, request: AnalyzeRequest, force_async: bool = False) -> tuple[str, JobInfo]:
        """
        Submit a new analysis job.
        
        Args:
            request: Analysis request parameters
            force_async: Force asynchronous execution
            
        Returns:
            Tuple of (job_id, job_info)
        """
        job_id = str(uuid.uuid4())
        
        # Create job info
        job_info = JobInfo(
            job_id=job_id,
            status=JobStatus.QUEUED,
            progress=None,
            submitted_at=datetime.now().isoformat(),
            started_at=None,
            finished_at=None,
            error=None
        )
        
        with self.job_lock:
            self.active_jobs[job_id] = job_info
        
        # Save job state
        self._save_job_state(job_id, job_info)
        
        # Start job execution in thread
        thread = threading.Thread(
            target=self._execute_job,
            args=(job_id, request),
            daemon=True
        )
        
        with self.job_lock:
            self.job_threads[job_id] = thread
        
        thread.start()
        
        logger.info(f"Submitted job {job_id}")
        return job_id, job_info
    
    def get_job_status(self, job_id: str) -> Optional[JobInfo]:
        """Get current status of a job."""
        with self.job_lock:
            job_info = self.active_jobs.get(job_id)
        
        if not job_info:
            # Try to load from disk
            job_info = self._load_job_state(job_id)
        
        return job_info
    
    def list_all_jobs(self, limit: int = 100, status: Optional[str] = None) -> List[JobInfo]:
        """List all jobs, optionally filtered by status."""
        jobs = []
        
        # Get active jobs
        with self.job_lock:
            jobs.extend(self.active_jobs.values())
        
        # Get jobs from disk (reports directory)
        try:
            reports_dir = self.storage_manager.get_reports_path()
            if reports_dir.exists():
                for report_file in reports_dir.glob("*.json"):
                    job_id = report_file.stem.replace("_enhanced", "")
                    if job_id not in self.active_jobs:
                        job_info = self._load_job_state(job_id)
                        if job_info:
                            jobs.append(job_info)
        except Exception as e:
            logger.warning(f"Error loading job history: {e}")
        
        # Filter by status if provided
        if status:
            jobs = [j for j in jobs if j.status.value == status]
        
        # Sort by submitted_at (newest first) and limit
        jobs.sort(key=lambda j: j.submitted_at, reverse=True)
        return jobs[:limit]
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a running or queued job."""
        with self.job_lock:
            job_info = self.active_jobs.get(job_id)
            
            if not job_info or job_info.status not in [JobStatus.QUEUED, JobStatus.RUNNING]:
                return False
            
            job_info.status = JobStatus.CANCELED
            job_info.finished_at = datetime.now().isoformat()
            
            self.active_jobs[job_id] = job_info
        
        self._save_job_state(job_id, job_info)
        self._emit_event(job_id, "finished", {"status": JobStatus.CANCELED.value})
        
        logger.info(f"Canceled job {job_id}")
        return True
    
    def rerun_job(self, job_id: str) -> Optional[tuple[str, JobInfo]]:
        """Re-run a job with the same parameters."""
        # For now, return None - would need to store original request
        # This would require storing the original AnalyzeRequest
        logger.warning(f"Job rerun not yet implemented for {job_id}")
        return None
    
    def get_analyzer_config(self) -> Dict[str, Any]:
        """Get current analyzer configuration."""
        return self.analyzer_config.copy()
    
    def update_analyzer_config(self, config: Dict[str, Any]) -> None:
        """Update analyzer configuration."""
        if "defaults" in config:
            self.analyzer_config["defaults"] = config["defaults"]
        if "rulesets" in config:
            self.analyzer_config["rulesets"].update(config["rulesets"])
        if "allow_list" in config:
            self.analyzer_config["allow_list"] = config["allow_list"]
        
        logger.info("Updated analyzer configuration")
    
    def add_event_callback(self, callback: Callable[[str, str, Dict], None]) -> None:
        """Add event callback for job progress/completion."""
        self.event_callbacks.append(callback)
    
    def cleanup_job(self, job_id: str) -> None:
        """Clean up job workspace and files."""
        try:
            # Remove workspace
            self.repo_fetcher.cleanup_workspace(job_id)
            
            # Remove job state file
            logs_dir = os.path.join(self.storage_base, "logs")
            job_state_file = os.path.join(logs_dir, f"{job_id}.json")
            if os.path.exists(job_state_file):
                os.remove(job_state_file)
            
            # Remove from active jobs
            with self.job_lock:
                self.active_jobs.pop(job_id, None)
                self.job_threads.pop(job_id, None)
            
            logger.info(f"Cleaned up job {job_id}")
        except Exception as e:
            logger.error(f"Error cleaning up job {job_id}: {e}")
    
    def _execute_job(self, job_id: str, request: AnalyzeRequest) -> None:
        """Execute a scanning job."""
        start_time = datetime.now()
        
        try:
            # Update job status
            self._update_job_status(job_id, JobStatus.RUNNING, started_at=start_time.isoformat())
            
            # Phase 1: Clone/Extract
            self._update_job_progress(job_id, JobPhase.CLONE, 10)
            workspace_path = self._fetch_source(job_id, request)
            
            # Phase 2: Sanitize workspace
            self._update_job_progress(job_id, JobPhase.CLONE, 20)
            self._sanitize_workspace(job_id, workspace_path, request)
            
            # Phase 3: Select and run analyzers
            analyzers = self._select_analyzers(request, workspace_path)
            analyzer_results = self._run_analyzers(job_id, analyzers, workspace_path)
            
            # Phase 4: Merge results and create report
            self._update_job_progress(job_id, JobPhase.MERGE, 85)
            report = self._create_report(job_id, request, analyzer_results, start_time)
            
            # Phase 5: Write report
            self._update_job_progress(job_id, JobPhase.WRITE, 95)
            self._save_report(job_id, report)
            
            # Complete job
            end_time = datetime.now()
            self._update_job_status(
                job_id, JobStatus.COMPLETED, 
                finished_at=end_time.isoformat()
            )
            
            # Emit completion event
            self._emit_event(job_id, "finished", {
                "job_id": job_id,
                "status": JobStatus.COMPLETED.value,
                "summary": report.summary.to_dict()
            })
            
            logger.info(f"Job {job_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}")
            
            self._update_job_status(
                job_id, JobStatus.FAILED,
                finished_at=datetime.now().isoformat(),
                error=str(e)
            )
            
            self._emit_event(job_id, "finished", {
                "job_id": job_id,
                "status": JobStatus.FAILED.value,
                "error": str(e)
            })
    
    def _fetch_source(self, job_id: str, request: AnalyzeRequest) -> str:
        """Fetch source code (GitHub or ZIP)."""
        if request.github_url:
            return self.repo_fetcher.fetch_github_repo(
                request.github_url,
                job_id,
                ref=request.ref,
                commit=request.commit
            )
        elif request.file:
            # Save uploaded file and extract
            temp_zip = os.path.join(self.storage_base, "workspace", f"{job_id}_upload.zip")
            with open(temp_zip, "wb") as f:
                f.write(request.file)
            
            try:
                workspace_path = self.repo_fetcher.extract_zip_archive(temp_zip, job_id)
                os.remove(temp_zip)  # Clean up temp file
                return workspace_path
            except Exception as e:
                if os.path.exists(temp_zip):
                    os.remove(temp_zip)
                raise e
        else:
            raise ValueError("Either github_url or file must be provided")
    
    def _sanitize_workspace(self, job_id: str, workspace_path: str, request: AnalyzeRequest) -> None:
        """Sanitize workspace by removing unwanted files."""
        include_patterns = request.get_include_patterns()
        exclude_patterns = request.get_exclude_patterns()
        
        stats = self.sanitizer.sanitize_workspace(
            workspace_path,
            include_patterns=include_patterns if include_patterns else None,
            exclude_patterns=exclude_patterns if exclude_patterns else None
        )
        
        logger.info(f"Job {job_id} workspace sanitization: {stats}")
    
    def _select_analyzers(self, request: AnalyzeRequest, workspace_path: str) -> List[str]:
        """Select which analyzers to run."""
        # Get requested analyzers or use defaults
        requested = request.get_analyzers_list()
        if not requested:
            requested = self.analyzer_config["defaults"]
        
        # Filter by allowed analyzers
        allowed = analyzer_registry.list_analyzers()
        filtered = filter_analyzers_by_config(requested, allowed)
        
        # Detect applicable analyzers based on workspace content
        applicable = detect_applicable_analyzers(workspace_path, filtered)
        
        logger.info(f"Selected analyzers: {applicable}")
        return applicable
    
    def _run_analyzers(self, job_id: str, analyzer_names: List[str], workspace_path: str) -> List[Any]:
        """Run analyzers in parallel."""
        results = []
        
        if not analyzer_names:
            logger.info(f"No analyzers to run for job {job_id}")
            return results
        
        # Run analyzers in parallel
        futures = []
        for i, analyzer_name in enumerate(analyzer_names):
            # Update progress
            progress = 30 + (50 * i // len(analyzer_names))
            self._update_job_progress(job_id, getattr(JobPhase, f"ANALYZE_{analyzer_name.upper()}", JobPhase.MERGE), progress)
            
            # Get analyzer instance
            analyzer = analyzer_registry.get_analyzer(analyzer_name, timeout_sec=300)
            if not analyzer:
                logger.warning(f"Analyzer {analyzer_name} not available")
                continue
            
            # Submit to thread pool
            future = self.executor.submit(analyzer.run_analysis, workspace_path)
            futures.append((analyzer_name, future))
        
        # Collect results
        for analyzer_name, future in futures:
            try:
                result = future.result(timeout=600)  # 10 minute timeout per analyzer
                results.append(result)
                logger.info(f"Analyzer {analyzer_name} completed for job {job_id}")
            except Exception as e:
                logger.error(f"Analyzer {analyzer_name} failed for job {job_id}: {e}")
                # Continue with other analyzers
        
        return results
    
    def _create_report(self, job_id: str, request: AnalyzeRequest, analyzer_results: List[Any], start_time: datetime) -> Report:
        """Create final report from analyzer results."""
        builder = ReportBuilder()
        
        # Add results from each analyzer
        for result in analyzer_results:
            builder.add_analyzer_result(result)
        
        # Create repo info
        repo_info = RepoInfo(
            source="github" if request.github_url else "zip",
            url=request.github_url,
            ref=request.ref,
            commit=request.commit
        )
        
        # Build report
        return builder.build_report(
            job_id=job_id,
            repo_info=repo_info,
            labels=request.get_labels_list(),
            start_time=start_time,
            end_time=datetime.now()
        )
    
    def _save_report(self, job_id: str, report: Report) -> None:
        """Save report to storage."""
        reports_dir = os.path.join(self.storage_base, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        report_file = os.path.join(reports_dir, f"{job_id}.json")
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report.to_json())
    
    def _update_job_status(self, job_id: str, status: JobStatus, **kwargs) -> None:
        """Update job status."""
        with self.job_lock:
            if job_id in self.active_jobs:
                job_info = self.active_jobs[job_id]
                job_info.status = status
                
                for key, value in kwargs.items():
                    if hasattr(job_info, key):
                        setattr(job_info, key, value)
                
                self.active_jobs[job_id] = job_info
        
        self._save_job_state(job_id, job_info)
    
    def _update_job_progress(self, job_id: str, phase: JobPhase, percent: int) -> None:
        """Update job progress."""
        with self.job_lock:
            if job_id in self.active_jobs:
                job_info = self.active_jobs[job_id]
                job_info.progress = JobProgress(phase=phase, percent=percent)
                self.active_jobs[job_id] = job_info
        
        # Emit progress event
        self._emit_event(job_id, "progress", {
            "phase": phase.value,
            "percent": percent
        })
    
    def _save_job_state(self, job_id: str, job_info: JobInfo) -> None:
        """Save job state to disk."""
        try:
            logs_dir = os.path.join(self.storage_base, "logs")
            os.makedirs(logs_dir, exist_ok=True)
            
            job_file = os.path.join(logs_dir, f"{job_id}.json")
            with open(job_file, "w", encoding="utf-8") as f:
                json.dump(job_info.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save job state for {job_id}: {e}")
    
    def _load_job_state(self, job_id: str) -> Optional[JobInfo]:
        """Load job state from disk."""
        try:
            job_file = os.path.join(self.storage_base, "logs", f"{job_id}.json")
            if not os.path.exists(job_file):
                return None
            
            with open(job_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Convert dict back to JobInfo
            progress_data = data.get("progress")
            progress = None
            if progress_data:
                progress = JobProgress(
                    phase=JobPhase(progress_data["phase"]),
                    percent=progress_data["percent"]
                )
            
            return JobInfo(
                job_id=data["job_id"],
                status=JobStatus(data["status"]),
                progress=progress,
                submitted_at=data["submitted_at"],
                started_at=data.get("started_at"),
                finished_at=data.get("finished_at"),
                error=data.get("error")
            )
        except Exception as e:
            logger.error(f"Failed to load job state for {job_id}: {e}")
            return None
    
    def _emit_event(self, job_id: str, event_type: str, data: Dict[str, Any]) -> None:
        """Emit event to registered callbacks."""
        for callback in self.event_callbacks:
            try:
                callback(job_id, event_type, data)
            except Exception as e:
                logger.error(f"Event callback failed: {e}")
    
    def _start_cleanup_thread(self) -> None:
        """Start background thread for cleaning up old jobs."""
        def cleanup_worker():
            while True:
                try:
                    self._cleanup_expired_jobs()
                    time.sleep(3600)  # Check every hour
                except Exception as e:
                    logger.error(f"Cleanup worker error: {e}")
                    time.sleep(60)  # Retry in 1 minute on error
        
        thread = threading.Thread(target=cleanup_worker, daemon=True)
        thread.start()
        logger.info("Started cleanup worker thread")
    
    def _cleanup_expired_jobs(self) -> None:
        """Clean up expired jobs (older than 7 days)."""
        cutoff_time = datetime.now() - timedelta(days=7)
        
        with self.job_lock:
            expired_jobs = []
            for job_id, job_info in self.active_jobs.items():
                submitted_time = datetime.fromisoformat(job_info.submitted_at)
                if submitted_time < cutoff_time and job_info.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELED]:
                    expired_jobs.append(job_id)
        
        for job_id in expired_jobs:
            logger.info(f"Cleaning up expired job: {job_id}")
            self.cleanup_job(job_id)


# Global orchestrator instance
orchestrator = None


def get_orchestrator(storage_base: str = None) -> JobOrchestrator:
    """Get global orchestrator instance."""
    global orchestrator
    if orchestrator is None and storage_base:
        orchestrator = JobOrchestrator(storage_base)
    return orchestrator