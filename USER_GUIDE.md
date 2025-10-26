# CodeAgent Vulnerability Scanner - User Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Usage](#basic-usage)
3. [AI-Enhanced Analysis](#ai-enhanced-analysis)
4. [Advanced Configuration](#advanced-configuration)
5. [Common Use Cases](#common-use-cases)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)

---

## Getting Started

### Prerequisites

Before using the scanner, ensure you have:

- **Python 3.11+** installed
- **OpenAI API Key** (for AI-enhanced features)
- **Git** installed (for repository scanning)
- **Internet connection** (for GitHub cloning and AI API)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/codeagent-scanner.git
   cd codeagent-scanner
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   # Create .env file
   cp .env.example .env
   
   # Edit .env and add your OpenAI API key
   OPENAI_API_KEY=sk-your-api-key-here
   ```

5. **Start the server:**
   ```bash
   cd codeagent-scanner
   $env:PORT=8000  # Windows PowerShell
   # export PORT=8000  # Linux/Mac
   python run.py
   ```

6. **Verify installation:**
   ```bash
   curl http://localhost:8000/health
   ```

   Expected response:
   ```json
   {
     "status": "ok",
     "version": "0.1.0",
     "ai_enabled": true
   }
   ```

---

## Basic Usage

### Scanning a GitHub Repository

#### Simple Scan

```bash
curl -X POST http://localhost:8000/analyze \
  -F "github_url=https://github.com/user/repo" \
  -F "ref=main"
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued"
}
```

#### Check Scan Status

```bash
curl http://localhost:8000/jobs/550e8400-e29b-41d4-a716-446655440000
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "progress": {
    "phase": "analyze:semgrep",
    "percent": 45
  }
}
```

#### Get Scan Results

```bash
curl http://localhost:8000/reports/550e8400-e29b-41d4-a716-446655440000
```

### Scanning a Local Project

```bash
# Create a ZIP of your project
zip -r myproject.zip /path/to/project -x "*/node_modules/*" "*/venv/*"

# Upload and scan
curl -X POST http://localhost:8000/analyze \
  -F "file=@myproject.zip"
```

### Filtering Files

```bash
# Scan only Python files
curl -X POST http://localhost:8000/analyze \
  -F "github_url=https://github.com/user/repo" \
  -F "include=**/*.py"

# Exclude test files
curl -X POST http://localhost:8000/analyze \
  -F "github_url=https://github.com/user/repo" \
  -F "exclude=**/tests/**,**/*_test.py"
```

---

## AI-Enhanced Analysis

### Overview

AI-enhanced analysis uses GPT-4 to provide:
- **Root cause analysis** of vulnerabilities
- **Concrete fix suggestions** with code examples
- **Security impact assessments**
- **Best practice recommendations**

### Enabling AI Features

1. **Set OpenAI API key:**
   ```bash
   # In .env file
   OPENAI_API_KEY=sk-your-key-here
   ENABLE_AI_ANALYSIS=true
   ```

2. **Configure AI settings:**
   ```bash
   # Choose AI model
   AI_MODEL=GPT_4  # Options: GPT_4, GPT_3_5_TURBO, GPT_4_32K
   
   # Set minimum severity for AI analysis
   AI_ANALYSIS_MIN_SEVERITY=high  # Options: critical, high, medium, low
   
   # Control concurrency
   MAX_CONCURRENT_AI_REVIEWS=2  # Range: 1-10
   
   # Set timeout
   AI_ANALYSIS_TIMEOUT_SEC=300  # Seconds
   ```

3. **Restart the server:**
   ```bash
   python run.py
   ```

### Getting AI-Enhanced Reports

```bash
# Run a scan
curl -X POST http://localhost:8000/analyze \
  -F "github_url=https://github.com/user/repo" \
  -F "ref=main"

# Get enhanced report (after scan completes)
curl http://localhost:8000/reports/550e8400-e29b-41d4-a716-446655440000/enhanced
```

**Enhanced Report Structure:**

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "enhanced_issues": [
    {
      "file": "src/auth.py",
      "original_issues": [
        {
          "tool": "bandit",
          "type": "B105",
          "severity": "high",
          "line": 15,
          "message": "Hardcoded password string"
        }
      ],
      "ai_analysis": {
        "analysis": "The code contains a hardcoded password which is a critical security vulnerability...",
        "suggested_fix": "import os\npassword = os.environ.get('DB_PASSWORD')",
        "explanation": "Store sensitive credentials in environment variables...",
        "security_impact": "Critical - Attackers with code access can immediately compromise the system.",
        "best_practices": [
          "Use environment variables",
          "Implement secret rotation",
          "Use secret management services"
        ]
      }
    }
  ],
  "summary": {
    "files_analyzed": 45,
    "issues_analyzed": 15,
    "ai_fixes_generated": 15
  }
}
```

### Runtime AI Configuration

Change AI settings without restarting:

```bash
# Check current settings
curl http://localhost:8000/config/ai

# Update settings
curl -X PATCH http://localhost:8000/config/ai \
  -H "Content-Type: application/json" \
  -d '{
    "model": "GPT_3_5_TURBO",
    "min_severity": "critical",
    "max_concurrent_reviews": 3,
    "timeout_sec": 180
  }'
```

### Cost Management

AI analysis uses OpenAI's API, which has associated costs. To manage expenses:

1. **Filter by Severity:**
   ```bash
   # Only analyze critical issues
   AI_ANALYSIS_MIN_SEVERITY=critical
   ```

2. **Use Faster Models:**
   ```bash
   # GPT-3.5 is cheaper than GPT-4
   AI_MODEL=GPT_3_5_TURBO
   ```

3. **Limit Concurrency:**
   ```bash
   # Process one issue at a time
   MAX_CONCURRENT_AI_REVIEWS=1
   ```

4. **Disable When Not Needed:**
   ```bash
   ENABLE_AI_ANALYSIS=false
   ```

5. **Monitor Usage:**
   ```bash
   # Check dashboard for AI usage stats
   curl http://localhost:8000/dashboard/stats
   ```

---

## Advanced Configuration

### Environment Variables

**Core Settings:**
```bash
# Storage
STORAGE_BASE=./storage
MAX_UPLOAD_SIZE=104857600  # 100MB

# Performance
MAX_CONCURRENT_JOBS=4
DEFAULT_TIMEOUT_SEC=600

# API
RATE_LIMIT_PER_MINUTE=60
PORT=8000
```

**AI Settings:**
```bash
# API Key (required)
OPENAI_API_KEY=sk-your-key-here

# Model Selection
AI_MODEL=GPT_4  # GPT_4, GPT_3_5_TURBO, GPT_4_32K

# Enable/Disable
ENABLE_AI_ANALYSIS=true

# Filtering
AI_ANALYSIS_MIN_SEVERITY=high  # critical, high, medium, low

# Performance
MAX_CONCURRENT_AI_REVIEWS=2
AI_ANALYSIS_TIMEOUT_SEC=300
```

### Analyzer Configuration

```bash
# Get current configuration
curl http://localhost:8000/config/analyzers

# Update configuration
curl -X PATCH http://localhost:8000/config/analyzers \
  -H "Content-Type: application/json" \
  -d '{
    "defaults": ["bandit", "semgrep"],
    "rulesets": {
      "semgrep": ["p/owasp-top-ten", "p/cwe-top-25"]
    }
  }'
```

### Custom Analyzer Selection

```bash
# Run specific analyzers
curl -X POST http://localhost:8000/analyze \
  -F "github_url=https://github.com/user/repo" \
  -F "analyzers=bandit,semgrep"

# Override timeout
curl -X POST http://localhost:8000/analyze \
  -F "github_url=https://github.com/user/repo" \
  -F "timeout_sec=300"
```

---

## Common Use Cases

### Use Case 1: Daily Security Audit

**Scenario:** Scan your main repository every day for new vulnerabilities.

```bash
#!/bin/bash
# daily_scan.sh

REPO_URL="https://github.com/your-org/your-repo"
SCANNER_URL="http://localhost:8000"

# Start scan
JOB_ID=$(curl -s -X POST $SCANNER_URL/analyze \
  -F "github_url=$REPO_URL" \
  -F "ref=main" \
  -F "labels=daily-audit,production" | jq -r '.job_id')

echo "Started scan: $JOB_ID"

# Wait for completion
while true; do
  STATUS=$(curl -s $SCANNER_URL/jobs/$JOB_ID | jq -r '.status')
  if [ "$STATUS" = "completed" ]; then
    break
  elif [ "$STATUS" = "failed" ]; then
    echo "Scan failed"
    exit 1
  fi
  sleep 10
done

# Get enhanced report
curl -s $SCANNER_URL/reports/$JOB_ID/enhanced > report_$(date +%Y%m%d).json

# Check for critical issues
CRITICAL=$(jq '.summary.severity_breakdown.critical' report_$(date +%Y%m%d).json)
if [ "$CRITICAL" -gt 0 ]; then
  echo "WARNING: $CRITICAL critical issues found!"
  # Send alert (Slack, email, etc.)
fi
```

### Use Case 2: Pull Request Scanning

**Scenario:** Scan every pull request before merging.

```bash
#!/bin/bash
# pr_scan.sh

PR_NUMBER=$1
REPO_URL="https://github.com/your-org/your-repo"

# Get PR branch
PR_BRANCH=$(gh pr view $PR_NUMBER --json headRefName -q '.headRefName')

# Scan the PR branch
JOB_ID=$(curl -s -X POST http://localhost:8000/analyze \
  -F "github_url=$REPO_URL" \
  -F "ref=$PR_BRANCH" \
  -F "labels=pr-$PR_NUMBER" | jq -r '.job_id')

# Wait and comment on PR
# ... (similar to Use Case 1)
```

### Use Case 3: Pre-Commit Hook

**Scenario:** Scan changed files before committing.

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Get changed Python files
CHANGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')

if [ -z "$CHANGED_FILES" ]; then
  exit 0
fi

# Create temp directory
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Copy changed files
for file in $CHANGED_FILES; do
  mkdir -p $TEMP_DIR/$(dirname $file)
  cp $file $TEMP_DIR/$file
done

# Scan
cd $TEMP_DIR
zip -r ../scan.zip .
cd -

JOB_ID=$(curl -s -X POST http://localhost:8000/analyze \
  -F "file=@$TEMP_DIR/../scan.zip" | jq -r '.job_id')

# Wait for results
# ... check for high/critical issues and block commit if found
```

### Use Case 4: Multi-Repository Dashboard

**Scenario:** Scan multiple repositories and view aggregate statistics.

```bash
#!/bin/bash
# scan_all_repos.sh

REPOS=(
  "https://github.com/org/repo1"
  "https://github.com/org/repo2"
  "https://github.com/org/repo3"
)

for repo in "${REPOS[@]}"; do
  REPO_NAME=$(basename $repo)
  echo "Scanning $REPO_NAME..."
  
  curl -X POST http://localhost:8000/analyze \
    -F "github_url=$repo" \
    -F "labels=org-scan,$REPO_NAME"
done

# View aggregate statistics
curl http://localhost:8000/dashboard/stats
```

---

## Troubleshooting

### Common Issues

#### 1. "No module named 'openai'"

**Problem:** OpenAI package not installed.

**Solution:**
```bash
pip install openai tiktoken
```

#### 2. "AI features disabled"

**Problem:** OpenAI API key not configured.

**Solution:**
```bash
# Add to .env
OPENAI_API_KEY=sk-your-key-here
ENABLE_AI_ANALYSIS=true

# Restart server
python run.py
```

#### 3. Port Already in Use

**Problem:** Port 8000 or 8080 is already in use.

**Solution:**
```bash
# Use different port
$env:PORT=9000  # Windows
# export PORT=9000  # Linux/Mac

python run.py
```

#### 4. "Rate limit exceeded"

**Problem:** Too many API requests.

**Solution:**
```bash
# Increase rate limit in .env
RATE_LIMIT_PER_MINUTE=120

# Or wait before retrying
sleep 60
```

#### 5. AI Analysis Timeout

**Problem:** AI analysis takes too long.

**Solution:**
```bash
# Increase timeout
AI_ANALYSIS_TIMEOUT_SEC=600

# Or use faster model
AI_MODEL=GPT_3_5_TURBO
```

#### 6. Import Errors in run.py

**Problem:** "No such file or directory: commit path"

**Solution:**
```python
# Ensure run.py has proper guard
if __name__ == "__main__":
    main()
```

### Debug Mode

Enable verbose logging:

```bash
# Set log level
export LOG_LEVEL=DEBUG

# Run server
python run.py
```

### Health Check

```bash
# Verify server is running
curl http://localhost:8000/health

# Check AI status
curl http://localhost:8000/config/ai

# View available analyzers
curl http://localhost:8000/tools
```

---

## Best Practices

### 1. Security

- **Never commit API keys** to version control
- Use `.env` files for sensitive configuration
- Rotate OpenAI API keys regularly
- Implement rate limiting for production

### 2. Performance

- Set appropriate concurrency limits based on your resources
- Use `AI_ANALYSIS_MIN_SEVERITY=high` to reduce API costs
- Enable caching for repeated scans of the same repository
- Monitor dashboard statistics to optimize configuration

### 3. CI/CD Integration

- Fail builds on critical vulnerabilities
- Use labels to track scan sources (`pr-123`, `daily-audit`)
- Store enhanced reports as build artifacts
- Set up webhooks for automatic notifications

### 4. Cost Management

- Start with `GPT_3_5_TURBO` for lower costs
- Only analyze `critical` and `high` severity issues
- Set `MAX_CONCURRENT_AI_REVIEWS=1` initially
- Monitor OpenAI usage dashboard

### 5. Workflow

1. **Run initial scan** with AI disabled to identify all issues
2. **Review severity distribution** using dashboard
3. **Enable AI analysis** for critical/high issues only
4. **Iterate on fixes** using AI suggestions
5. **Re-scan** to verify fixes
6. **Automate** with CI/CD integration

### 6. Report Management

- Use labels to organize scans (`team:backend`, `env:prod`)
- Download enhanced reports for offline review
- Archive old reports to save storage
- Share reports with development teams

---

## Additional Resources

- **API Documentation:** See `README-scanner.md` for complete API reference
- **Implementation Plan:** See `IMPLEMENTATION_PLAN.md` for architecture details
- **Test Documentation:** See `PHASE_4_COMPLETE.md` for testing information
- **GitHub Repository:** https://github.com/your-org/codeagent-scanner

---

## Support

For issues, questions, or contributions:

1. **Check the documentation** first
2. **Search existing issues** on GitHub
3. **Create a new issue** with detailed information
4. **Include logs** and error messages

---

## Version History

- **v0.1.0** (2024-10-17)
  - Initial release
  - AI-enhanced analysis with GPT-4
  - Dashboard statistics
  - Runtime configuration API
  - Comprehensive test suite (41 tests, 100% passing)

---

*Last updated: October 2024*
