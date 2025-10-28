"""Main FastAPI application for CodeAgent Vulnerability Scanner."""

import asyncio
import json
import logging
import os
import hmac
import hashlib
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
import tempfile
import shutil

import httpx
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Response, File, Form, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_202_ACCEPTED, HTTP_400_BAD_REQUEST
import uvicorn

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our modules
from pipeline.orchestrator import get_orchestrator, JobOrchestrator
from pipeline.report_schema import (
    AnalyzeRequest, AnalyzeResponse, JobInfo, Report, ReportListResponse, 
    ReportListItem, ToolsResponse, HealthResponse, ErrorResponse,
    WebhookConfig, WebhookPayload, AnalyzerConfig, SeveritySummary
)
from analyzers.base import analyzer_registry
from integration.camel_bridge import CamelBridge

# Register all analyzers
from analyzers.semgrep_runner import SemgrepAnalyzer
from analyzers.bandit_runner import BanditAnalyzer
from analyzers.depcheck_runner import DepCheckAnalyzer

# Configuration
STORAGE_BASE = os.getenv("STORAGE_BASE", "./storage")
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", 50 * 1024 * 1024))  # 50MB
MAX_CONCURRENT_JOBS = int(os.getenv("MAX_CONCURRENT_JOBS", 2))
API_VERSION = "0.1.0"

# Ensure storage directories exist
for subdir in ["workspace", "reports", "logs"]:
    os.makedirs(os.path.join(STORAGE_BASE, subdir), exist_ok=True)

# Initialize FastAPI app
app = FastAPI(
    title="CodeAgent Vulnerability Scanner API",
    version=API_VERSION,
    description="Security vulnerability scanner for source code repositories"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
orchestrator: Optional[JobOrchestrator] = None
agent_bridge: Optional[CamelBridge] = None
webhooks: Dict[str, WebhookConfig] = {}
sse_clients: Dict[str, List] = {}  # job_id -> list of response objects


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    global orchestrator, agent_bridge
    orchestrator = get_orchestrator(STORAGE_BASE)
    
    # Initialize AI agent bridge (multi-agent system)
    try:
        agent_bridge = CamelBridge()
        logger.info("Multi-Agent Bridge (CAMEL) initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize Multi-Agent Bridge: {e}")
        agent_bridge = None
    
    # Register event callback for webhooks and SSE
    orchestrator.add_event_callback(handle_job_event)
    
    logger.info(f"CodeAgent Scanner API v{API_VERSION} started")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    logger.info("CodeAgent Scanner API shutting down")


def handle_job_event(job_id: str, event_type: str, data: Dict[str, Any]):
    """Handle job events for webhooks, SSE, and AI analysis."""
    # Handle SSE clients
    if job_id in sse_clients:
        event_data = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
        for response in sse_clients[job_id][:]:  # Copy list to avoid modification during iteration
            try:
                # Note: This is simplified - in practice you'd need proper async handling
                pass  # SSE would be handled differently in real implementation
            except Exception as e:
                logger.error(f"Failed to send SSE event: {e}")
                sse_clients[job_id].remove(response)
    
    # Handle webhooks and AI analysis for completion events
    if event_type == "finished" and data.get("status") == "completed":
        asyncio.create_task(process_completed_job(job_id, data))


async def process_completed_job(job_id: str, data: Dict[str, Any]):
    """Process completed job: run AI analysis and deliver webhooks."""
    # First, trigger AI analysis if enabled
    enable_ai = os.getenv("ENABLE_AI_ANALYSIS", "true").lower() == "true"
    
    if enable_ai and agent_bridge:
        try:
            # Get full report
            report_file = os.path.join(STORAGE_BASE, "reports", f"{job_id}.json")
            if os.path.exists(report_file):
                with open(report_file, 'r') as f:
                    report = json.load(f)
                
                # Get workspace path
                workspace_path = os.path.join(STORAGE_BASE, "workspace", job_id)
                
                # Check if there are high/critical issues to analyze
                summary = report.get('summary', {})
                if summary.get('high', 0) > 0 or summary.get('critical', 0) > 0:
                    logger.info(f"Starting AI analysis for job {job_id}")
                    
                    # Run AI analysis
                    enhanced_report = await agent_bridge.process_vulnerabilities(
                        job_id=job_id,
                        report=report,
                        workspace_path=workspace_path
                    )
                    
                    # Save enhanced report
                    enhanced_file = os.path.join(STORAGE_BASE, "reports", f"{job_id}_enhanced.json")
                    with open(enhanced_file, 'w') as f:
                        json.dump(enhanced_report, f, indent=2)
                    
                    logger.info(f"AI analysis completed for job {job_id}")
                else:
                    logger.info(f"No high/critical issues found for job {job_id}, skipping AI analysis")
            
        except Exception as e:
            logger.error(f"AI analysis failed for job {job_id}: {e}")
    
    # Then deliver webhooks
    await deliver_webhooks(job_id, data)


async def deliver_webhooks(job_id: str, data: Dict[str, Any]):
    """Deliver webhook notifications."""
    for webhook_id, webhook in webhooks.items():
        if "report.created" in webhook.events and webhook.active:
            try:
                # Get job info for payload
                job_info = orchestrator.get_job_status(job_id)
                if not job_info:
                    continue
                
                # Create payload
                payload = WebhookPayload(
                    job_id=job_id,
                    repo=None,  # Would need to get from job
                    summary=SeveritySummary(),  # Would need to get from report
                    report_url=f"/reports/{job_id}"
                )
                
                # Send webhook
                await send_webhook(webhook, payload.to_dict())
                
            except Exception as e:
                logger.error(f"Failed to deliver webhook {webhook_id}: {e}")


async def send_webhook(webhook: WebhookConfig, payload: Dict[str, Any]):
    """Send webhook HTTP POST."""
    try:
        headers = {
            "Content-Type": "application/json",
            "X-Event": "report.created"
        }
        
        payload_json = json.dumps(payload)
        
        # Add signature if secret is configured
        if webhook.secret:
            signature = hmac.new(
                webhook.secret.encode(),
                payload_json.encode(),
                hashlib.sha256
            ).hexdigest()
            headers["X-Signature"] = f"sha256={signature}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                webhook.url,
                headers=headers,
                content=payload_json,
                timeout=30.0
            )
            
            if response.status_code >= 200 and response.status_code < 300:
                logger.info(f"Webhook delivered successfully to {webhook.url}")
            else:
                logger.warning(f"Webhook delivery failed: {response.status_code}")
                
    except Exception as e:
        logger.error(f"Webhook delivery error: {e}")


# Helper functions
def validate_analyze_request(
    github_url: Optional[str] = None,
    file: Optional[UploadFile] = None
) -> None:
    """Validate analyze request parameters."""
    if not github_url and not file:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "INVALID_INPUT", "message": "Either github_url or file must be provided"}}
        )
    
    if github_url and file:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "INVALID_INPUT", "message": "Cannot provide both github_url and file"}}
        )
    
    if file and file.size and file.size > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail={"error": {"code": "PAYLOAD_TOO_LARGE", "message": f"File too large. Max size: {MAX_UPLOAD_SIZE} bytes"}}
        )


async def create_analyze_request(
    github_url: Optional[str] = Form(None),
    ref: Optional[str] = Form(None),
    commit: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    include: Optional[str] = Form(None),
    exclude: Optional[str] = Form(None),
    analyzers: Optional[str] = Form(None),
    timeout_sec: Optional[int] = Form(None),
    labels: Optional[str] = Form(None)
) -> AnalyzeRequest:
    """Create AnalyzeRequest from form data."""
    validate_analyze_request(github_url, file)
    
    file_bytes = None
    if file:
        file_bytes = await file.read()
    
    return AnalyzeRequest(
        github_url=github_url,
        ref=ref,
        commit=commit,
        file=file_bytes,
        include=include,
        exclude=exclude,
        analyzers=analyzers,
        timeout_sec=timeout_sec,
        labels=labels
    )


def error_response(code: str, message: str, details: Optional[Dict] = None) -> JSONResponse:
    """Create standardized error response."""
    error = ErrorResponse(code=code, message=message, details=details)
    status_code = {
        "INVALID_INPUT": 400,
        "UNAUTHORIZED": 401,
        "FORBIDDEN": 403,
        "NOT_FOUND": 404,
        "CONFLICT": 409,
        "PAYLOAD_TOO_LARGE": 413,
        "RATE_LIMIT": 429,
        "TIMEOUT": 504,
        "INTERNAL": 500
    }.get(code, 500)
    
    return JSONResponse(content=error.to_dict(), status_code=status_code)


# API Endpoints

@app.get("/health")
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="ok", version=API_VERSION)


@app.get("/tools")
async def get_tools() -> ToolsResponse:
    """Get available analyzers and versions."""
    available = analyzer_registry.list_analyzers()
    versions = analyzer_registry.get_versions()
    defaults = orchestrator.get_analyzer_config()["defaults"]
    
    return ToolsResponse(
        available=available,
        default=defaults,
        versions=versions
    )


@app.post("/analyze")
async def analyze(request: AnalyzeRequest = Depends(create_analyze_request)) -> AnalyzeResponse:
    """Submit analysis job (sync or async based on estimated time)."""
    if not orchestrator:
        return error_response("INTERNAL", "Service not initialized")
    
    try:
        job_id, job_info = orchestrator.submit_job(request, force_async=False)
        
        # For now, always return 202 (async) - sync detection would need more logic
        return AnalyzeResponse(job_id=job_id, status="running")
        
    except Exception as e:
        logger.error(f"Failed to submit job: {e}")
        return error_response("INTERNAL", str(e))


@app.post("/analyze-async")  
async def analyze_async(request: AnalyzeRequest = Depends(create_analyze_request)) -> AnalyzeResponse:
    """Submit analysis job (always async)."""
    if not orchestrator:
        return error_response("INTERNAL", "Service not initialized")
    
    try:
        job_id, job_info = orchestrator.submit_job(request, force_async=True)
        return AnalyzeResponse(job_id=job_id, status="queued")
        
    except Exception as e:
        logger.error(f"Failed to submit async job: {e}")
        return error_response("INTERNAL", str(e))


@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str) -> JobInfo:
    """Get job status and progress."""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Service not initialized")
    
    job_info = orchestrator.get_job_status(job_id)
    if not job_info:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job_info


@app.delete("/jobs/{job_id}")
async def cancel_job(job_id: str) -> Dict[str, str]:
    """Cancel a running or queued job."""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Service not initialized")
    
    success = orchestrator.cancel_job(job_id)
    if not success:
        raise HTTPException(status_code=409, detail="Cannot cancel job")
    
    return {"job_id": job_id, "status": "canceling"}


@app.post("/jobs/{job_id}/rerun")
async def rerun_job(job_id: str) -> AnalyzeResponse:
    """Re-run a job with the same parameters."""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Service not initialized")
    
    result = orchestrator.rerun_job(job_id)
    if not result:
        raise HTTPException(status_code=404, detail="Cannot rerun job")
    
    new_job_id, job_info = result
    return AnalyzeResponse(job_id=new_job_id, status="queued")


@app.get("/reports/{job_id}")
async def get_report(job_id: str) -> Report:
    """Get full scan report."""
    report_file = os.path.join(STORAGE_BASE, "reports", f"{job_id}.json")
    
    if not os.path.exists(report_file):
        raise HTTPException(status_code=404, detail="Report not found")
    
    try:
        with open(report_file, "r", encoding="utf-8") as f:
            report_data = json.load(f)
        return report_data
    except Exception as e:
        logger.error(f"Failed to load report {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to load report")


@app.get("/reports")
async def list_reports(
    page: int = 1,
    limit: int = 20,
    severity: Optional[str] = None,
    tool: Optional[str] = None,
    repo: Optional[str] = None,
    since: Optional[str] = None,
    until: Optional[str] = None,
    label: Optional[str] = None
) -> ReportListResponse:
    """List and filter reports with pagination."""
    # This is a simplified implementation - would need proper database for filtering
    reports_dir = os.path.join(STORAGE_BASE, "reports")
    
    if not os.path.exists(reports_dir):
        return ReportListResponse(items=[], page=page, limit=limit, total=0)
    
    # Get all report files
    report_files = [f for f in os.listdir(reports_dir) if f.endswith('.json')]
    
    # Load and filter reports (simplified)
    items = []
    for report_file in report_files:
        try:
            with open(os.path.join(reports_dir, report_file), "r") as f:
                report_data = json.load(f)
            
            # Create list item
            item = ReportListItem(
                job_id=report_data["job_id"],
                repo_url=report_data["meta"]["repo"].get("url"),
                generated_at=report_data["meta"]["generated_at"],
                summary=SeveritySummary(**report_data["summary"]),
                tools=report_data["meta"]["tools"],
                labels=report_data["meta"]["labels"]
            )
            items.append(item)
        except Exception as e:
            logger.warning(f"Failed to load report {report_file}: {e}")
    
    # Sort by generated_at (newest first)
    items.sort(key=lambda x: x.generated_at, reverse=True)
    
    # Paginate
    start = (page - 1) * limit
    end = start + limit
    paginated_items = items[start:end]
    
    return ReportListResponse(
        items=paginated_items,
        page=page,
        limit=limit,
        total=len(items)
    )


@app.get("/reports/{job_id}/summary")
async def get_report_summary(job_id: str) -> Dict[str, Any]:
    """Get lightweight report summary."""
    report_file = os.path.join(STORAGE_BASE, "reports", f"{job_id}.json")
    
    if not os.path.exists(report_file):
        raise HTTPException(status_code=404, detail="Report not found")
    
    try:
        with open(report_file, "r", encoding="utf-8") as f:
            report_data = json.load(f)
        
        return {
            "job_id": job_id,
            "summary": report_data["summary"]
        }
    except Exception as e:
        logger.error(f"Failed to load report summary {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to load report summary")


@app.get("/reports/{job_id}/enhanced")
async def get_enhanced_report(job_id: str) -> Dict[str, Any]:
    """Get AI-enhanced scan report with fixes."""
    enhanced_file = os.path.join(STORAGE_BASE, "reports", f"{job_id}_enhanced.json")
    
    if not os.path.exists(enhanced_file):
        raise HTTPException(status_code=404, detail="Enhanced report not available yet")
    
    try:
        with open(enhanced_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load enhanced report {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to load enhanced report")


@app.get("/events/{job_id}")
async def get_job_events(job_id: str) -> StreamingResponse:
    """Server-Sent Events stream for job progress."""
    # This is a simplified SSE implementation
    async def event_generator():
        # Register client for this job
        if job_id not in sse_clients:
            sse_clients[job_id] = []
        
        # Send initial status
        job_info = orchestrator.get_job_status(job_id) if orchestrator else None
        if job_info:
            yield f"data: {json.dumps(job_info.to_dict())}\n\n"
        
        # Keep connection open for updates
        # In practice, you'd implement proper SSE with connection management
        import asyncio
        await asyncio.sleep(60)  # Keep connection open for 1 minute
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/webhooks/register")
async def register_webhook(
    url: str,
    events: List[str],
    secret: Optional[str] = None
) -> Dict[str, str]:
    """Register webhook for events."""
    webhook_id = f"wh_{uuid.uuid4().hex[:8]}"
    
    webhook = WebhookConfig(
        id=webhook_id,
        url=url,
        events=events,
        secret=secret,
        created_at=datetime.now().isoformat()
    )
    
    webhooks[webhook_id] = webhook
    
    return {"id": webhook_id}


@app.delete("/webhooks/{webhook_id}")
async def delete_webhook(webhook_id: str) -> Dict[str, str]:
    """Unregister webhook."""
    if webhook_id not in webhooks:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    del webhooks[webhook_id]
    return {"id": webhook_id, "status": "deleted"}


@app.get("/config/analyzers")
async def get_analyzer_config() -> AnalyzerConfig:
    """Get analyzer configuration."""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Service not initialized")
    
    config = orchestrator.get_analyzer_config()
    return AnalyzerConfig(**config)


@app.patch("/config/analyzers")
async def update_analyzer_config(config: Dict[str, Any]) -> Dict[str, bool]:
    """Update analyzer configuration."""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Service not initialized")
    
    orchestrator.update_analyzer_config(config)
    return {"ok": True}


@app.get("/config/ai")
async def get_ai_config() -> Dict[str, Any]:
    """Get AI analysis configuration."""
    return {
        "enabled": os.getenv("ENABLE_AI_ANALYSIS", "true").lower() == "true",
        "model": os.getenv("AI_MODEL", "GPT_4"),
        "min_severity": os.getenv("AI_ANALYSIS_MIN_SEVERITY", "high"),
        "max_concurrent_reviews": int(os.getenv("MAX_CONCURRENT_AI_REVIEWS", "1")),
        "timeout_sec": int(os.getenv("AI_ANALYSIS_TIMEOUT_SEC", "300")),
        "bridge_initialized": agent_bridge is not None
    }


@app.patch("/config/ai")
async def update_ai_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Update AI analysis configuration (runtime only)."""
    updated = {}
    
    # Note: In production, these should be persisted to a database
    # For now, we only update environment variables for the current session
    
    if "enabled" in config:
        os.environ["ENABLE_AI_ANALYSIS"] = str(config["enabled"]).lower()
        updated["enabled"] = config["enabled"]
    
    if "model" in config:
        valid_models = ["GPT_4", "GPT_3_5_TURBO", "GPT_4_32K"]
        if config["model"] in valid_models:
            os.environ["AI_MODEL"] = config["model"]
            updated["model"] = config["model"]
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid model. Must be one of: {', '.join(valid_models)}"
            )
    
    if "min_severity" in config:
        valid_severities = ["critical", "high", "medium", "low"]
        if config["min_severity"] in valid_severities:
            os.environ["AI_ANALYSIS_MIN_SEVERITY"] = config["min_severity"]
            updated["min_severity"] = config["min_severity"]
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid severity. Must be one of: {', '.join(valid_severities)}"
            )
    
    if "max_concurrent_reviews" in config:
        try:
            value = int(config["max_concurrent_reviews"])
            if value < 1 or value > 10:
                raise ValueError("Must be between 1 and 10")
            os.environ["MAX_CONCURRENT_AI_REVIEWS"] = str(value)
            updated["max_concurrent_reviews"] = value
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    if "timeout_sec" in config:
        try:
            value = int(config["timeout_sec"])
            if value < 60 or value > 600:
                raise ValueError("Must be between 60 and 600 seconds")
            os.environ["AI_ANALYSIS_TIMEOUT_SEC"] = str(value)
            updated["timeout_sec"] = value
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    logger.info(f"AI configuration updated: {updated}")
    return {
        "ok": True,
        "updated": updated,
        "message": "Configuration updated successfully (runtime only, not persisted)"
    }


@app.get("/dashboard/stats")
async def get_dashboard_stats() -> Dict[str, Any]:
    """Get overall statistics for dashboard."""
    reports_dir = os.path.join(STORAGE_BASE, "reports")
    
    # Initialize stats
    stats = {
        "total_scans": 0,
        "ai_enhanced_reports": 0,
        "severity_distribution": {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        },
        "active_jobs": 0,
        "recent_scans": []
    }
    
    # Check if reports directory exists
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir, exist_ok=True)
        return stats
    
    try:
        report_files = os.listdir(reports_dir)
        
        # Count reports
        regular_reports = [f for f in report_files if f.endswith('.json') and not f.endswith('_enhanced.json')]
        enhanced_reports = [f for f in report_files if f.endswith('_enhanced.json')]
        
        stats["total_scans"] = len(regular_reports)
        stats["ai_enhanced_reports"] = len(enhanced_reports)
        
        # Calculate severity distribution and collect recent scans
        recent_scans = []
        
        for report_file in regular_reports:
            try:
                report_path = os.path.join(reports_dir, report_file)
                with open(report_path, 'r') as f:
                    report = json.load(f)
                
                # Update severity totals
                summary = report.get('summary', {})
                for severity in stats["severity_distribution"]:
                    stats["severity_distribution"][severity] += summary.get(severity, 0)
                
                # Collect recent scan info
                job_id = report.get('job_id', report_file.replace('.json', ''))
                recent_scans.append({
                    'job_id': job_id,
                    'generated_at': report.get('meta', {}).get('generated_at', ''),
                    'total_issues': sum(summary.values()),
                    'has_ai_analysis': f"{job_id}_enhanced.json" in enhanced_reports
                })
                
            except Exception as e:
                logger.warning(f"Failed to process report {report_file}: {e}")
                continue
        
        # Sort by generated_at and take 10 most recent
        recent_scans.sort(key=lambda x: x['generated_at'], reverse=True)
        stats["recent_scans"] = recent_scans[:10]
        
        # Get active jobs count
        if orchestrator:
            stats["active_jobs"] = len(orchestrator.active_jobs)
        
    except Exception as e:
        logger.error(f"Failed to generate dashboard stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate statistics")
    
    return stats


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": "HTTP_ERROR", "message": exc.detail}}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL", "message": "Internal server error"}}
    )


if __name__ == "__main__":
    # Run with uvicorn for development
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )