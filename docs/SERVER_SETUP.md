# CodeAgent Vulnerability Scanner - Server Setup Guide

## ✅ Server Successfully Configured

### Quick Start

```powershell
# Set the port (Windows reserves 8080, use 8000 instead)
$env:PORT="8000"

# Navigate to scanner directory and start server
cd D:\MinorProject\codeagent-scanner
python run.py
```

### Server Information

- **Running on**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Version**: 0.1.0

### Dependencies Installed

All required dependencies have been successfully installed:
- ✅ `openai` - OpenAI API client
- ✅ `tenacity` - Retry logic for API calls
- ✅ `tiktoken` - Token counting for GPT models
- ✅ `Flask` & `Flask-SocketIO` - Web framework dependencies
- ✅ `markdown` - Markdown processing
- ✅ `httpx` - Async HTTP client
- ✅ `aiofiles` - Async file operations

### Phase 3 API Endpoints - ALL WORKING ✅

#### 1. GET /config/ai
Retrieve current AI configuration:
```json
{
  "enabled": true,
  "model": "GPT_4",
  "min_severity": "high",
  "max_concurrent_reviews": 1,
  "timeout_sec": 300,
  "bridge_initialized": true
}
```

#### 2. PATCH /config/ai
Update AI settings at runtime:
```bash
curl -X PATCH http://localhost:8000/config/ai \
  -H "Content-Type: application/json" \
  -d '{"min_severity": "critical"}'
```

#### 3. GET /dashboard/stats
Get scan statistics and metrics:
```json
{
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
```

### Test Results

All automated tests passed:
```
✅ Test 0: Health Check - PASSED
✅ Test 1: GET /config/ai - PASSED
✅ Test 2.1: Valid update - PASSED
✅ Test 2.2: Invalid model validation - PASSED
✅ Test 2.3: Multiple field update - PASSED
✅ Test 3: GET /dashboard/stats - PASSED
```

### Known Warnings (Non-Critical)

- ⚠️ **Semgrep not installed** - Optional static analysis tool. Install with:
  ```powershell
  pip install semgrep
  ```

### Issues Fixed

1. **Module Import Error**: Fixed `run.py` to prevent execution when imported
   - Changed import path in `agent_bridge.py`
   - Added `if __name__ == "__main__":` guard
   - Wrapped execution code in `main()` function

2. **Port Binding Error**: Windows reserves port 8080
   - Solution: Use port 8000 instead
   - Set via environment variable: `$env:PORT="8000"`

3. **Missing Dependencies**: Installed all required packages
   - Added to `requirements.txt`
   - Installed via pip

### Environment Variables

Configure in `.env` file or set as environment variables:

```bash
# Server Configuration
PORT=8000
HOST=0.0.0.0

# AI Configuration
OPENAI_API_KEY=your_api_key_here
AI_MODEL=GPT_4
ENABLE_AI_ANALYSIS=true
AI_ANALYSIS_MIN_SEVERITY=high
MAX_CONCURRENT_AI_REVIEWS=1
AI_ANALYSIS_TIMEOUT_SEC=300

# Storage
STORAGE_BASE=./storage
MAX_UPLOAD_SIZE=52428800
MAX_CONCURRENT_JOBS=2
```

### Testing the API

Run the automated test suite:
```powershell
python test_phase3_api.py
```

Or test manually with curl:
```powershell
# Health check
curl http://localhost:8000/health

# Get AI config
curl http://localhost:8000/config/ai

# Update AI config
curl -X PATCH http://localhost:8000/config/ai ^
  -H "Content-Type: application/json" ^
  -d "{\"min_severity\": \"critical\"}"

# Get statistics
curl http://localhost:8000/dashboard/stats
```

### Next Steps

Phase 3 is complete! Ready for:
- **Phase 4**: Testing & Validation
- **Phase 5**: Documentation updates
- **Phase 6**: Deployment configuration

---

**Status**: ✅ All systems operational
**Last Updated**: October 26, 2025
