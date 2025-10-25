# CodeAgent Vulnerability Scanner

A comprehensive security vulnerability scanner API for source code repositories. This service analyzes GitHub repositories and uploaded ZIP archives using multiple security tools (Semgrep, Bandit, dependency checkers) and provides normalized, actionable vulnerability reports.

## Features

- **Multi-tool Analysis**: Integrates Semgrep, Bandit, and dependency vulnerability scanners
- **Source Flexibility**: Supports GitHub URLs and ZIP file uploads
- **Async Processing**: Background job execution with progress tracking
- **Real-time Updates**: Server-Sent Events (SSE) for live progress monitoring
- **Webhook Integration**: HTTP callbacks for job completion notifications
- **Comprehensive Reports**: Normalized JSON reports with severity classification
- **Filtering & Search**: Advanced filtering by severity, tool, repository, and labels
- **RESTful API**: Complete REST API with OpenAPI documentation

## Quick Start

### Using Docker (Recommended)

```bash
# Build the container
docker build -t codeagent-scanner .

# Run the service
docker run -p 8080:8080 -v $(pwd)/storage:/app/storage codeagent-scanner

# The API will be available at http://localhost:8080
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Install security tools
pip install semgrep bandit pip-audit

# Set up environment
cp .env.example .env

# Run the service
python api/app.py
```

## API Usage

### Health Check
```bash
curl http://localhost:8080/health
```

### Scan a GitHub Repository
```bash
curl -X POST http://localhost:8080/analyze \\
  -F "github_url=https://github.com/user/repo" \\
  -F "analyzers=bandit,semgrep,depcheck"
```

### Upload and Scan ZIP File
```bash
curl -X POST http://localhost:8080/analyze \\
  -F "file=@project.zip" \\
  -F "include=src/**/*.py"
```

### Check Job Status
```bash
curl http://localhost:8080/jobs/{job_id}
```

### Get Report
```bash
curl http://localhost:8080/reports/{job_id}
```

### Live Progress (SSE)
```bash
curl -H "Accept: text/event-stream" http://localhost:8080/events/{job_id}
```

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
| `/reports` | GET | List/filter reports |
| `/reports/{job_id}/summary` | GET | Report summary only |
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

## Configuration

### Environment Variables

See `.env.example` for all available configuration options:

- `STORAGE_BASE`: Directory for workspaces and reports
- `MAX_UPLOAD_SIZE`: Maximum ZIP file size (bytes)
- `MAX_CONCURRENT_JOBS`: Concurrent job limit
- `DEFAULT_TIMEOUT_SEC`: Default analyzer timeout
- `RATE_LIMIT_PER_MINUTE`: API rate limiting

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
└── requirements.txt
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest
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
      - "8080:8080"
    volumes:
      - ./storage:/app/storage
    environment:
      - STORAGE_BASE=/app/storage
      - MAX_CONCURRENT_JOBS=4
```

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