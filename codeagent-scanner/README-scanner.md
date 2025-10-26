# CodeAgent Vulnerability Scanner

A comprehensive security vulnerability scanner API for source code repositories. This service analyzes GitHub repositories and uploaded ZIP archives using multiple security tools (Semgrep, Bandit, dependency checkers) and provides normalized, actionable vulnerability reports.

## Features

- **Multi-tool Analysis**: Integrates Semgrep, Bandit, and dependency vulnerability scanners
- **AI-Enhanced Analysis** ✨: GPT-4 powered security analysis for critical/high severity issues
- **Intelligent Fix Suggestions**: AI-generated code fixes and security recommendations
- **Source Flexibility**: Supports GitHub URLs and ZIP file uploads
- **Async Processing**: Background job execution with progress tracking
- **Real-time Updates**: Server-Sent Events (SSE) for live progress monitoring
- **Webhook Integration**: HTTP callbacks for job completion notifications
- **Comprehensive Reports**: Normalized JSON reports with severity classification
- **Enhanced Reports**: AI-analyzed reports with detailed explanations and fixes
- **Runtime Configuration**: Dynamic AI configuration without service restart
- **Dashboard Statistics**: Real-time metrics and scan statistics
- **Filtering & Search**: Advanced filtering by severity, tool, repository, and labels
- **RESTful API**: Complete REST API with OpenAPI documentation

## Quick Start

### Prerequisites

- Python 3.12+
- OpenAI API key (for AI-enhanced analysis)
- Git (for repository cloning)

### Using Docker (Recommended)

```bash
# Build the container
docker build -t codeagent-scanner .

# Run the service with AI support
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_key_here \
  -v $(pwd)/storage:/app/storage \
  codeagent-scanner

# The API will be available at http://localhost:8000
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Install security tools (optional - analyzer-specific)
pip install semgrep bandit pip-audit

# Set up environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run the service
cd codeagent-scanner
export PORT=8000  # Windows: $env:PORT="8000"
python run.py

# API documentation: http://localhost:8000/docs
# Health check: http://localhost:8000/health
```

## API Usage

### Health Check
```bash
curl http://localhost:8000/health
```

### Scan a GitHub Repository
```bash
curl -X POST http://localhost:8000/analyze \
  -F "github_url=https://github.com/user/repo" \
  -F "analyzers=bandit,semgrep,depcheck"
```

### Upload and Scan ZIP File
```bash
curl -X POST http://localhost:8000/analyze \
  -F "file=@project.zip" \
  -F "include=src/**/*.py"
```

### Check Job Status
```bash
curl http://localhost:8000/jobs/{job_id}
```

### Get Standard Report
```bash
curl http://localhost:8000/reports/{job_id}
```

### Get AI-Enhanced Report ✨
```bash
# Get vulnerability report with AI-generated fixes and recommendations
curl http://localhost:8000/reports/{job_id}/enhanced
```

### Get AI Configuration
```bash
# Check current AI settings
curl http://localhost:8000/config/ai
```

### Update AI Configuration
```bash
# Change AI model or settings at runtime
curl -X PATCH http://localhost:8000/config/ai \
  -H "Content-Type: application/json" \
  -d '{
    "model": "GPT_4",
    "min_severity": "critical",
    "max_concurrent_reviews": 2,
    "timeout_sec": 180
  }'
```

### Get Dashboard Statistics
```bash
# View scan statistics and metrics
curl http://localhost:8000/dashboard/stats
```

### Live Progress (SSE)
```bash
curl -H "Accept: text/event-stream" http://localhost:8000/events/{job_id}
```

## AI-Enhanced Analysis ✨

### Overview

The scanner integrates with OpenAI's GPT-4 to provide intelligent analysis of security vulnerabilities. When enabled, the AI reviews critical and high-severity issues to provide:

- **Root Cause Analysis**: Detailed explanation of why the vulnerability exists
- **Security Impact Assessment**: Potential risks and attack vectors
- **Code Fix Suggestions**: Concrete code changes to remediate issues
- **Best Practice Recommendations**: Security guidelines and prevention strategies

### How It Works

1. **Automated Scanning**: Traditional tools (Semgrep, Bandit) identify vulnerabilities
2. **AI Filtering**: Only critical/high severity issues are sent to AI (cost control)
3. **Intelligent Review**: GPT-4 analyzes code context and generates recommendations
4. **Enhanced Report**: Results include both scan data and AI insights

### AI Configuration

AI analysis is controlled via environment variables and runtime API:

```bash
# Environment variables (.env file)
OPENAI_API_KEY=sk-...              # Required for AI features
AI_MODEL=GPT_4                      # GPT_4, GPT_3_5_TURBO, or GPT_4_32K
ENABLE_AI_ANALYSIS=true             # Enable/disable AI features
AI_ANALYSIS_MIN_SEVERITY=high       # Minimum severity for AI analysis
MAX_CONCURRENT_AI_REVIEWS=1         # Concurrent AI requests
AI_ANALYSIS_TIMEOUT_SEC=300         # Timeout per AI analysis
```

### Runtime Configuration

Update AI settings without restarting the service:

```bash
# Check current configuration
curl http://localhost:8000/config/ai

# Update settings
curl -X PATCH http://localhost:8000/config/ai \
  -H "Content-Type: application/json" \
  -d '{
    "model": "GPT_3_5_TURBO",
    "min_severity": "critical",
    "max_concurrent_reviews": 2
  }'
```

### Cost Control

To manage OpenAI API costs:

1. **Severity Filtering**: Set `AI_ANALYSIS_MIN_SEVERITY` to `critical` or `high`
2. **Concurrency Limits**: Control `MAX_CONCURRENT_AI_REVIEWS` (1-10)
3. **Timeouts**: Set reasonable `AI_ANALYSIS_TIMEOUT_SEC` values
4. **Disable When Needed**: Set `ENABLE_AI_ANALYSIS=false` to disable

### Dashboard Metrics

Monitor AI usage and scan statistics:

```bash
curl http://localhost:8000/dashboard/stats
```

Returns scan counts, severity distribution, AI enhancement stats, and recent activity.

## API Endpoints

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/health` | GET | Service health check |
| `/tools` | GET | Available analyzers and versions |
| `/analyze` | POST | Submit scan (sync/async) |
| `/analyze-async` | POST | Submit scan (always async) |
| `/jobs/{job_id}` | GET | Job status and progress |
| `/jobs/{job_id}` | DELETE | Cancel job |
| `/jobs/{job_id}/rerun` | POST | Re-run job |
| `/reports/{job_id}` | GET | Full scan report |
| `/reports/{job_id}/enhanced` | GET | ✨ AI-enhanced report with fixes |
| `/reports` | GET | List/filter reports |
| `/reports/{job_id}/summary` | GET | Report summary only |
| `/config/ai` | GET | ✨ Get AI configuration |
| `/config/ai` | PATCH | ✨ Update AI configuration |
| `/dashboard/stats` | GET | ✨ Get scan statistics |
| `/events/{job_id}` | GET | SSE progress stream |
| `/webhooks/register` | POST | Register webhook |
| `/webhooks/{id}` | DELETE | Unregister webhook |
| `/config/analyzers` | GET | Analyzer configuration |
| `/config/analyzers` | PATCH | Update configuration |

## Request Parameters

### Analyze Request (Form Data)

- `github_url` (string): GitHub repository URL
- `ref` (string): Branch or tag to checkout
- `commit` (string): Specific commit SHA
- `file` (file): ZIP archive upload
- `include` (string): Comma-separated glob patterns to include
- `exclude` (string): Comma-separated glob patterns to exclude
- `analyzers` (string): Comma-separated analyzer names
- `timeout_sec` (integer): Per-tool timeout override
- `labels` (string): Comma-separated labels for tracking

## Response Formats

### Job Status Response
```json
{
  "job_id": "uuid",
  "status": "queued|running|completed|failed|canceled",
  "progress": {
    "phase": "clone|analyze:tool|merge|write",
    "percent": 65
  },
  "submitted_at": "2023-10-17T14:30:00Z",
  "started_at": "2023-10-17T14:30:05Z",
  "finished_at": null,
  "error": null
}
```

### Report Structure
```json
{
  "job_id": "uuid",
  "meta": {
    "tools": ["bandit", "semgrep"],
    "repo": {
      "source": "github",
      "url": "https://github.com/user/repo",
      "ref": "main",
      "commit": null
    },
    "generated_at": "2023-10-17T14:35:00Z",
    "duration_ms": 45000,
    "labels": ["team:security"]
  },
  "summary": {
    "critical": 0,
    "high": 3,
    "medium": 7,
    "low": 12
  },
  "files": [
    {
      "path": "src/app.py",
      "issues": [
        {
          "tool": "bandit",
          "type": "B608",
          "message": "Possible SQL injection",
          "severity": "high",
          "file": "src/app.py",
          "line": 42,
          "rule_id": "B608",
          "suggestion": "Use parameterized queries"
        }
      ]
    }
  ]
}
```

### AI-Enhanced Report Structure ✨

When AI analysis is enabled, use `/reports/{job_id}/enhanced` to get reports with AI-generated fixes:

```json
{
  "job_id": "uuid",
  "status": "complete",
  "enhanced_issues": [
    {
      "file": "src/auth.py",
      "issues_analyzed": 2,
      "original_issues": [
        {
          "tool": "bandit",
          "type": "B105",
          "severity": "high",
          "line": 15,
          "message": "Hardcoded password string",
          "code_snippet": "password = 'admin123'"
        }
      ],
      "ai_analysis": {
        "analysis": "The code contains a hardcoded password which is a critical security vulnerability. Hardcoded credentials in source code can be extracted by anyone with access to the codebase...",
        "suggested_fix": "import os\npassword = os.environ.get('DB_PASSWORD')\nif not password:\n    raise ValueError('DB_PASSWORD environment variable not set')",
        "explanation": "Store sensitive credentials in environment variables or secure secret management systems like AWS Secrets Manager, Azure Key Vault, or HashiCorp Vault. Never commit credentials to source control.",
        "security_impact": "Critical - Attackers with code access can immediately compromise the system. If code is public or leaked, credentials are exposed to anyone.",
        "best_practices": [
          "Use environment variables for configuration",
          "Implement secret rotation policies",
          "Use secret management services",
          "Add .env to .gitignore",
          "Audit code for other hardcoded secrets"
        ]
      }
    }
  ],
  "summary": {
    "total_files_scanned": 45,
    "files_with_issues": 12,
    "issues_analyzed_by_ai": 15,
    "ai_fixes_generated": 15,
    "severity_breakdown": {
      "critical": 2,
      "high": 13,
      "medium": 27,
      "low": 43
    },
    "ai_analysis_duration_ms": 4500,
    "status": "complete"
  },
  "meta": {
    "ai_model_used": "GPT_4",
    "min_severity_analyzed": "high",
    "generated_at": "2023-10-17T14:35:00Z"
  }
}
```

## Configuration

### Environment Variables

See `.env.example` for all available configuration options:

**Core Settings:**
- `STORAGE_BASE`: Directory for workspaces and reports
- `MAX_UPLOAD_SIZE`: Maximum ZIP file size (bytes)
- `MAX_CONCURRENT_JOBS`: Concurrent job limit
- `DEFAULT_TIMEOUT_SEC`: Default analyzer timeout
- `RATE_LIMIT_PER_MINUTE`: API rate limiting

**AI-Enhanced Analysis Settings:** ✨
- `OPENAI_API_KEY`: OpenAI API key (required for AI features)
- `AI_MODEL`: AI model to use (GPT_4, GPT_3_5_TURBO, GPT_4_32K)
- `ENABLE_AI_ANALYSIS`: Enable/disable AI analysis (true/false)
- `AI_ANALYSIS_MIN_SEVERITY`: Minimum severity for AI review (critical/high/medium/low)
- `MAX_CONCURRENT_AI_REVIEWS`: Max concurrent AI API calls (1-10)
- `AI_ANALYSIS_TIMEOUT_SEC`: Timeout per AI analysis request (seconds)

### Analyzer Configuration

Configure default analyzers, rulesets, and URL allowlists via the `/config/analyzers` endpoint:

```json
{
  "defaults": ["bandit", "semgrep", "depcheck"],
  "rulesets": {
    "semgrep": ["p/owasp-top-ten", "p/security-audit"],
    "bandit": []
  },
  "allow_list": ["https://github.com/", "https://gitlab.com/"]
}
```

## Supported Analyzers

| Tool | Languages | Description |
|------|-----------|-------------|
| **Semgrep** | Multi-language | Static analysis with security rules |
| **Bandit** | Python | Python security linter |
| **Dependency Check** | Python, Node.js, etc. | Vulnerability scanning for dependencies |

## Webhook Integration

Register webhooks to receive notifications when scans complete:

```bash
curl -X POST http://localhost:8080/webhooks/register \\
  -H "Content-Type: application/json" \\
  -d '{
    "url": "https://your-service.com/webhook",
    "events": ["report.created"],
    "secret": "optional-hmac-secret"
  }'
```

Webhook payloads include HMAC signatures for verification when a secret is provided.

## Security Considerations

- **Sandboxed Execution**: All analysis runs in isolated workspaces
- **No Code Execution**: Only static analysis - never executes repository code
- **Path Validation**: Prevents path traversal attacks in ZIP files
- **Resource Limits**: File size, count, and time limits prevent abuse
- **URL Allowlisting**: Restrict GitHub/GitLab hosts as needed

## Development

### Project Structure
```
codeagent-scanner/
├── api/
│   └── app.py              # FastAPI application
├── analyzers/
│   ├── base.py             # Base analyzer framework
│   ├── detect.py           # Analyzer detection logic
│   ├── semgrep_runner.py   # Semgrep integration
│   ├── bandit_runner.py    # Bandit integration
│   └── depcheck_runner.py  # Dependency checking
├── integration/            # ✨ AI Integration Layer
│   ├── agent_bridge.py     # OpenAI GPT-4 bridge
│   └── prompts.py          # AI prompt templates
├── ingestion/
│   ├── fetch_repo.py       # GitHub cloning & ZIP extraction
│   └── sanitize.py         # Workspace sanitization
├── pipeline/
│   ├── orchestrator.py     # Job orchestration
│   └── report_schema.py    # Data models
├── storage/
│   ├── workspace/          # Per-job workspaces
│   ├── reports/            # JSON reports
│   └── logs/               # Job state logs
├── tests/                  # ✨ Test Suite
│   ├── test_agent_bridge.py    # AI integration tests (15 tests)
│   └── test_integration.py     # API tests (26 tests)
└── requirements.txt
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
cd codeagent-scanner
pytest tests/ -v

# Run specific test file
pytest tests/test_agent_bridge.py -v
pytest tests/test_integration.py -v

# Test Results (Phase 4 Complete)
# - 15 AgentBridge unit tests (AI integration)
# - 26 API integration tests  
# - 41 total tests, 100% passing
```

### Adding New Analyzers

1. Create analyzer class inheriting from `BaseAnalyzer`
2. Implement required methods (`name`, `version`, `is_applicable`, `run_analysis`)
3. Register with `analyzer_registry.register(YourAnalyzer)`
4. Add to detection logic in `detect.py`

## Deployment

### Docker Compose

```yaml
version: '3.8'
services:
  scanner:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./storage:/app/storage
    environment:
      # Core Configuration
      - STORAGE_BASE=/app/storage
      - MAX_CONCURRENT_JOBS=4
      - PORT=8000
      
      # AI-Enhanced Analysis ✨
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - AI_MODEL=GPT_4
      - ENABLE_AI_ANALYSIS=true
      - AI_ANALYSIS_MIN_SEVERITY=high
      - MAX_CONCURRENT_AI_REVIEWS=2
      - AI_ANALYSIS_TIMEOUT_SEC=300
```

**Important**: Create a `.env` file with your `OPENAI_API_KEY` before running `docker-compose up`.

### Kubernetes

See deployment examples in the `k8s/` directory (if provided).

## Monitoring & Observability

- **Health Endpoint**: `/health` for load balancer checks
- **Structured Logging**: JSON logs with correlation IDs
- **Metrics**: Job counts, durations, error rates (extend as needed)
- **Progress Events**: Real-time job status via SSE

## Rate Limiting & Quotas

- 60 requests/minute per API key
- 2 concurrent jobs per API key
- 50MB upload size limit
- 10,000 files per workspace
- 10-minute default timeout per analyzer

## Error Handling

All errors follow a consistent format:

```json
{
  "error": {
    "code": "INVALID_INPUT|NOT_FOUND|TIMEOUT|etc",
    "message": "Human readable description",
    "details": {"field": "specific_field"}
  }
}
```

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Support

For questions or issues:
- Create a GitHub issue for bugs/features
- Check API documentation at `/docs` endpoint
- Review error codes in responses

---

**Note**: This scanner performs static analysis only and never executes code from analyzed repositories. It's designed for CI/CD integration and automated security review workflows.