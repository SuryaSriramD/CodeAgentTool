# CodeAgent Vulnerability Scanner - Complete Workflow 🔒

**Date:** October 31, 2025  
**Version:** 2.0 (Enhanced with AI-Powered Grouping)  
**Status:** ✅ Production Ready

---

## 📋 Table of Contents
1. [System Architecture](#system-architecture)
2. [Complete User Workflow](#complete-user-workflow)
3. [Backend Processing Pipeline](#backend-processing-pipeline)
4. [AI Enhancement Pipeline](#ai-enhancement-pipeline)
5. [Frontend Report Display](#frontend-report-display)
6. [Export Functionality](#export-functionality)
7. [API Endpoints Reference](#api-endpoints-reference)
8. [Data Flow Diagram](#data-flow-diagram)

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                               │
│                   (Next.js 16 - Port 3000)                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐   │
│  │ Dashboard  │  │   Jobs     │  │  Reports   │  │    API     │   │
│  │   Page     │  │   Page     │  │   Page     │  │ Playground │   │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘   │
└────────────────────────────┬────────────────────────────────────────┘
                             │ HTTP/REST API
                             │ (JSON Communication)
┌────────────────────────────▼────────────────────────────────────────┐
│                      BACKEND API SERVER                              │
│                   (FastAPI - Port 8000)                             │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    API Endpoints Layer                        │  │
│  │  /analyze | /reports | /enhance | /health | /tools          │  │
│  └────────────────────┬─────────────────────────────────────────┘  │
│                       │                                              │
│  ┌────────────────────▼─────────────────────────────────────────┐  │
│  │              Job Orchestrator (Pipeline Manager)              │  │
│  │  • Job Queue Management  • Thread Pool (max 4 workers)       │  │
│  │  • Status Tracking       • Progress Monitoring                │  │
│  └────────────────────┬─────────────────────────────────────────┘  │
│                       │                                              │
│  ┌────────────────────▼─────────────────────────────────────────┐  │
│  │           Scanning Phase (Security Analyzers)                 │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐                   │  │
│  │  │ Semgrep  │  │  Bandit  │  │DepCheck  │                   │  │
│  │  │ (OWASP)  │  │ (Python) │  │ (Node)   │                   │  │
│  │  └──────────┘  └──────────┘  └──────────┘                   │  │
│  └────────────────────┬─────────────────────────────────────────┘  │
│                       │ Raw Vulnerability Data                       │
│                       │ (Issues with severity/line/file)             │
│  ┌────────────────────▼─────────────────────────────────────────┐  │
│  │            Report Builder (Aggregation)                       │  │
│  │  • Merge results from all analyzers                          │  │
│  │  • Deduplicate issues                                         │  │
│  │  • Calculate severity summary (Critical/High/Med/Low)        │  │
│  │  • Generate base report JSON                                  │  │
│  └────────────────────┬─────────────────────────────────────────┘  │
│                       │ Base Report                                  │
│                       │ {job_id, issues[], severity_summary, ...}   │
│  ┌────────────────────▼─────────────────────────────────────────┐  │
│  │          AI Enhancement Phase (Optional)                      │  │
│  │  ┌────────────────────────────────────────────────────────┐  │  │
│  │  │  CamelBridge / SimpleAIAnalyzer                        │  │  │
│  │  │  • Analyze ALL severity levels (Low→Critical)          │  │  │
│  │  │  • Sort issues by severity (Critical first)            │  │  │
│  │  │  • Generate AI fixes for each vulnerability            │  │  │
│  │  │  • Create grouped recommendations by priority          │  │  │
│  │  └────────────────────────────────────────────────────────┘  │  │
│  │                                                                  │  │
│  │  Output Structure:                                              │  │
│  │  {                                                               │  │
│  │    "ai_analysis": {                                             │  │
│  │      "fixes": [...],                                            │  │
│  │      "fixes_by_severity": {                                     │  │
│  │        "critical": [...],                                       │  │
│  │        "high": [...],                                           │  │
│  │        "medium": [...],                                         │  │
│  │        "low": [...]                                             │  │
│  │      },                                                          │  │
│  │      "severity_summary": {critical: 0, high: 3, medium: 13...},│  │
│  │      "recommendations_by_priority": {                           │  │
│  │        "high": [{title, description, priority}, ...],          │  │
│  │        "medium": [{title, description, priority}, ...],        │  │
│  │        "low": [{title, description, priority}, ...]            │  │
│  │      }                                                           │  │
│  │    }                                                             │  │
│  │  }                                                               │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────────┘
                             │ Enhanced Report JSON
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│                    STORAGE LAYER (File System)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │  Workspace   │  │   Reports    │  │     Logs     │             │
│  │  (Repos)     │  │   (JSON)     │  │   (Debug)    │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Complete User Workflow

### **Phase 1: Scan Submission**

```
USER ACTION                    SYSTEM RESPONSE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Open Dashboard              → Display scan form
   (http://localhost:3000)     

2. Enter Repository URL        → Validate URL format
   Example:                    → Check allowlist
   https://github.com/user/repo

3. Select Analyzers            → Show available tools:
   ☑ Semgrep (OWASP)             • Semgrep (default)
   ☑ Bandit (Python)             • Bandit (if Python detected)
   ☑ DepCheck (Dependencies)     • DepCheck (if package.json)

4. Click "Start Scan"          → POST /analyze
                               → Generate job_id
                               → Return: {job_id: "6caf9b01..."}
                               → Redirect to Jobs page

5. Job Status Page             → WebSocket connection established
   Loading... 0%               → Real-time progress updates
                               → Shows current phase
```

### **Phase 2: Backend Scanning**

```
BACKEND PROCESSING PIPELINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1: Repository Ingestion
┌────────────────────────────────────────┐
│ Phase: INGESTION                       │
│ Progress: 10%                          │
│                                        │
│ • Clone repository to workspace        │
│ • Path: ./storage/workspace/{job_id}  │
│ • Sanitize workspace (remove .git)     │
│ • Detect project language/framework    │
└────────────────────────────────────────┘
         │
         ▼
Step 2: Security Analysis
┌────────────────────────────────────────┐
│ Phase: ANALYSIS                        │
│ Progress: 30% → 80%                    │
│                                        │
│ Parallel Execution (ThreadPool):      │
│ ┌──────────┐  ┌──────────┐           │
│ │ Semgrep  │  │  Bandit  │           │
│ │ Running  │  │ Running  │           │
│ │ OWASP    │  │ B201,    │           │
│ │ rules    │  │ B301,    │           │
│ │ p/sec... │  │ B302     │           │
│ └────┬─────┘  └────┬─────┘           │
│      │             │                  │
│      ▼             ▼                  │
│   [Issues]     [Issues]               │
│   • SQL Inject  • eval()              │
│   • XSS         • pickle              │
│   • CSRF        • exec()              │
└────────────────────────────────────────┘
         │
         ▼
Step 3: Report Aggregation
┌────────────────────────────────────────┐
│ Phase: REPORTING                       │
│ Progress: 85%                          │
│                                        │
│ Report Builder:                        │
│ • Merge all analyzer results          │
│ • Deduplicate by (file, line, rule)   │
│ • Sort by severity                     │
│ • Calculate statistics:                │
│   - Total issues: 16                   │
│   - Critical: 0                        │
│   - High: 3                            │
│   - Medium: 13                         │
│   - Low: 0                             │
│                                        │
│ Save: ./storage/reports/{job_id}.json │
└────────────────────────────────────────┘
         │
         ▼
Step 4: Completion
┌────────────────────────────────────────┐
│ Phase: COMPLETE                        │
│ Progress: 100%                         │
│                                        │
│ Status: COMPLETED                      │
│ Duration: 45.2 seconds                 │
│                                        │
│ Auto-trigger: AI Enhancement?          │
│ → YES (since issues found)             │
└────────────────────────────────────────┘
```

### **Phase 3: AI Enhancement (Automatic)**

```
AI ANALYSIS PIPELINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Trigger: Scan completion with issues found
Endpoint: POST /reports/{job_id}/enhance (auto-called)

Step 1: Load Base Report
┌────────────────────────────────────────┐
│ Read: ./storage/reports/{job_id}.json │
│                                        │
│ Input: Base report with 16 issues     │
│ • File paths, line numbers             │
│ • Severity levels                      │
│ • Vulnerability types                  │
│ • Original code snippets               │
└────────────────────────────────────────┘
         │
         ▼
Step 2: AI Analysis (SimpleAIAnalyzer)
┌────────────────────────────────────────────────────────────┐
│ CamelBridge → SimpleAIAnalyzer                             │
│                                                            │
│ 🤖 OpenAI GPT-4 API Call                                  │
│                                                            │
│ Input Prompt:                                              │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ "Analyze these security vulnerabilities:              │ │
│ │                                                        │ │
│ │  🔴 CRITICAL SEVERITY ISSUES (0 issues)               │ │
│ │                                                        │ │
│ │  🟠 HIGH SEVERITY ISSUES (3 issues)                   │ │
│ │  1. SQL Injection in auth.py:45                       │ │
│ │     Code: cursor.execute(f'SELECT * FROM...')         │ │
│ │  2. Eval usage in calculator.py:12                    │ │
│ │  3. Hardcoded credentials in config.py:8              │ │
│ │                                                        │ │
│ │  🟡 MEDIUM SEVERITY ISSUES (13 issues)                │ │
│ │  1. Missing input validation in form.py:23            │ │
│ │  2. Weak random number generation in token.py:56      │ │
│ │  ... (11 more issues)                                 │ │
│ │                                                        │ │
│ │  For each issue:                                      │ │
│ │  1. Generate secure code fix                          │ │
│ │  2. Explain the security risk                         │ │
│ │  3. Provide remediation steps                         │ │
│ │                                                        │ │
│ │  Also provide general recommendations grouped by:     │ │
│ │  - HIGH priority (critical security practices)        │ │
│ │  - MEDIUM priority (important improvements)           │ │
│ │  - LOW priority (nice-to-have enhancements)          │ │
│ └────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
         │
         ▼
Step 3: Response Processing & Grouping
┌──────────────────────────────────────────────────────────────┐
│ Parse AI Response & Apply Grouping Logic                     │
│                                                               │
│ A. Process Fixes (app.py Lines 195-230)                      │
│    For each vulnerability:                                    │
│    {                                                          │
│      file: "auth.py",                                         │
│      line: 45,                                                │
│      severity: "high",          ← Added from base report     │
│      vulnerability_type: "sqli", ← Added from base report    │
│      original_code: "cursor.execute(f'SELECT...')",          │
│      fixed_code: "cursor.execute('SELECT... WHERE id=?', id)",│
│      explanation: "Use parameterized queries to prevent..."   │
│    }                                                          │
│                                                               │
│    Group by severity:                                         │
│    fixes_by_severity = {                                      │
│      "critical": [],                                          │
│      "high": [fix1, fix2, fix3],      ← 3 high fixes        │
│      "medium": [fix4...fix16],         ← 13 medium fixes     │
│      "low": []                                                │
│    }                                                          │
│                                                               │
│ B. Process Recommendations (app.py Lines 210-230)             │
│    Parse AI general advice:                                   │
│    [                                                          │
│      {                                                        │
│        title: "Avoid using eval()",                          │
│        description: "Never use eval() or similar functions...",│
│        priority: "high"                                       │
│      },                                                       │
│      {                                                        │
│        title: "Input Validation and Sanitization",           │
│        description: "Implement strict input validation...",   │
│        priority: "high"                                       │
│      },                                                       │
│      ... 15 more recommendations                              │
│    ]                                                          │
│                                                               │
│    Group by priority:                                         │
│    recommendations_by_priority = {                            │
│      "high": [rec1...rec8],     ← 8 high priority           │
│      "medium": [rec9...rec15],  ← 7 medium priority          │
│      "low": [rec16, rec17]      ← 2 low priority             │
│    }                                                          │
│                                                               │
│ C. Calculate Summary                                          │
│    severity_summary = {                                       │
│      critical: 0,                                             │
│      high: 3,                                                 │
│      medium: 13,                                              │
│      low: 0,                                                  │
│      total: 16                                                │
│    }                                                          │
└──────────────────────────────────────────────────────────────┘
         │
         ▼
Step 4: Save Enhanced Report
┌────────────────────────────────────────┐
│ Update report with ai_analysis field:  │
│                                        │
│ {                                      │
│   job_id: "6caf9b01...",              │
│   status: "completed",                 │
│   issues: [...],                       │
│   ai_analysis: {                       │
│     fixes: [...],                      │
│     fixes_by_severity: {...},         │
│     severity_summary: {...},          │
│     recommendations: [...],            │
│     recommendations_by_priority: {...},│
│     status: "completed"                │
│   }                                    │
│ }                                      │
│                                        │
│ Save: ./storage/reports/{job_id}.json │
└────────────────────────────────────────┘
```

### **Phase 4: Frontend Display**

```
USER VIEWS ENHANCED REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Navigate to Reports Page
   GET /reports → Display all completed scans

2. Click "View Report" for job
   GET /reports/{job_id} → Load full report JSON

3. Report Display Components:

   ┌─────────────────────────────────────────────────────┐
   │ 📊 Summary Section                                  │
   │                                                     │
   │ Total Issues: 16                                    │
   │ 🔴 Critical: 0   🟠 High: 3                        │
   │ 🟡 Medium: 13    ⚪ Low: 0                         │
   │                                                     │
   │ AI Analysis: ✅ Completed                          │
   │ • 16 AI-Generated Fixes                            │
   │ • 17 Security Recommendations                      │
   └─────────────────────────────────────────────────────┘

   ┌─────────────────────────────────────────────────────┐
   │ 🔧 AI-Generated Fixes (Grouped by Severity)        │
   │                                                     │
   │ 🟠 HIGH SEVERITY (3 fixes)                         │
   │ ┌─────────────────────────────────────────────┐   │
   │ │ Fix #1: auth.py Line 45                     │   │
   │ │ Vulnerability: SQL Injection                │   │
   │ │                                             │   │
   │ │ ❌ Original (Vulnerable):                   │   │
   │ │ cursor.execute(f'SELECT * FROM users...')   │   │
   │ │                                             │   │
   │ │ ✅ Fixed (Secure):                          │   │
   │ │ cursor.execute('SELECT * FROM users WHERE...│   │
   │ │                                             │   │
   │ │ 💡 Explanation:                             │   │
   │ │ Use parameterized queries to prevent SQL... │   │
   │ └─────────────────────────────────────────────┘   │
   │                                                     │
   │ 🟡 MEDIUM SEVERITY (13 fixes)                      │
   │ [Similar cards for each medium fix...]             │
   │                                                     │
   └─────────────────────────────────────────────────────┘

   ┌─────────────────────────────────────────────────────┐
   │ 📋 Security Recommendations (Grouped by Priority)  │
   │                                                     │
   │ 🔴 HIGH PRIORITY (8 recommendations)               │
   │ • Avoid using eval()                               │
   │   Never use eval() or similar functions that...    │
   │                                                     │
   │ • Input Validation and Sanitization                │
   │   Implement strict input validation for all...     │
   │                                                     │
   │ • Use Prepared Statements                          │
   │   Always use prepared statements or...             │
   │                                                     │
   │ 🟡 MEDIUM PRIORITY (7 recommendations)             │
   │ • Regular Security Audits                          │
   │   Conduct regular security audits and...           │
   │                                                     │
   │ • Dependency Management                            │
   │   Keep all dependencies up to date...              │
   │                                                     │
   │ ⚪ LOW PRIORITY (2 recommendations)                │
   │ • Documentation                                     │
   │   Maintain comprehensive security docs...          │
   │                                                     │
   └─────────────────────────────────────────────────────┘

4. Export Options
   ┌─────────────────────────────────────────────────────┐
   │ 📥 Download Report As:                             │
   │ [HTML] [Markdown] [CSV] [JSON]                     │
   └─────────────────────────────────────────────────────┘
```

---

## 📤 Export Functionality

### **HTML Export** (`export-utils.ts` Lines 670-765)

**Structure:**
```html
<!DOCTYPE html>
<html>
<head>
  <style>/* Professional styling */</style>
</head>
<body>
  <h1>Security Scan Report - Enhanced</h1>
  
  <section class="summary">
    <h2>📊 Summary</h2>
    <ul>
      <li>Total Issues: 16</li>
      <li>Critical: 0, High: 3, Medium: 13, Low: 0</li>
    </ul>
  </section>

  <section class="fixes">
    <h2>🔧 AI-Generated Fixes</h2>
    
    <!-- HIGH SEVERITY -->
    <div style="margin: 20px 0;">
      <h4 style="color: #dc2626;">🔴 HIGH SEVERITY (3 fixes)</h4>
      <ul>
        <li>
          <strong>File:</strong> auth.py (Line 45)<br/>
          <strong>Type:</strong> SQL Injection<br/>
          <strong>Fix:</strong> Use parameterized queries...
        </li>
      </ul>
    </div>
    
    <!-- MEDIUM SEVERITY -->
    <div style="margin: 20px 0;">
      <h4 style="color: #f59e0b;">🟡 MEDIUM SEVERITY (13 fixes)</h4>
      <!-- Similar structure -->
    </div>
  </section>

  <section class="recommendations">
    <h2>📋 Security Recommendations</h2>
    
    <!-- HIGH PRIORITY -->
    <div style="margin: 20px 0;">
      <h4 style="color: #dc2626;">🔴 HIGH PRIORITY (8 recommendations)</h4>
      <ul>
        <li>
          <strong>Avoid using eval()</strong><br/>
          <span style="color: #6b7280;">
            Never use eval() or similar functions...
          </span>
        </li>
      </ul>
    </div>
    
    <!-- MEDIUM PRIORITY -->
    <div style="margin: 20px 0;">
      <h4 style="color: #f59e0b;">🟡 MEDIUM PRIORITY (7 recommendations)</h4>
      <!-- Similar structure -->
    </div>
    
    <!-- LOW PRIORITY -->
    <div style="margin: 20px 0;">
      <h4 style="color: #6b7280;">⚪ LOW PRIORITY (2 recommendations)</h4>
      <!-- Similar structure -->
    </div>
  </section>
</body>
</html>
```

### **Markdown Export** (`export-utils.ts` Lines 808-850)

```markdown
# Security Scan Report - Enhanced

## 📊 Summary
- Total Issues: 16
- Critical: 0, High: 3, Medium: 13, Low: 0

## 🔧 AI-Generated Fixes

### 🔴 HIGH SEVERITY (3 fixes)
- **auth.py (Line 45)**
  - Type: SQL Injection
  - Fix: Use parameterized queries to prevent SQL injection...

### 🟡 MEDIUM SEVERITY (13 fixes)
- **form.py (Line 23)**
  - Type: Missing Input Validation
  - Fix: Implement strict input validation...

## 📋 Security Recommendations

### 🔴 HIGH PRIORITY (8 recommendations)
- **Avoid using eval()**
  Never use eval() or similar functions that execute arbitrary code...

- **Input Validation and Sanitization**
  Implement strict input validation for all user inputs...

### 🟡 MEDIUM PRIORITY (7 recommendations)
- **Regular Security Audits**
  Conduct regular security audits and penetration testing...

### ⚪ LOW PRIORITY (2 recommendations)
- **Documentation**
  Maintain comprehensive security documentation...
```

### **CSV Export** (`export-utils.ts` Lines 875-895)

```csv
"Security Scan Report - Enhanced"
"Repository","https://github.com/user/repo"
"Scanned At","2025-10-31T10:30:00Z"

"Summary"
"Total Issues","16"
"Critical","0"
"High","3"
"Medium","13"
"Low","0"

"AI-Generated Fixes"
"Severity","File","Line","Type","Fix"
"HIGH","auth.py","45","SQL Injection","Use parameterized queries..."
"HIGH","calculator.py","12","Dangerous Function","Replace eval() with safe..."
"HIGH","config.py","8","Hardcoded Credentials","Use environment variables..."
"MEDIUM","form.py","23","Input Validation","Implement input validation..."

"Security Recommendations"
"Priority","Title","Description"
"HIGH","Avoid using eval()","Never use eval() or similar functions..."
"HIGH","Input Validation and Sanitization","Implement strict input validation..."
"MEDIUM","Regular Security Audits","Conduct regular security audits..."
"LOW","Documentation","Maintain comprehensive security docs..."
```

---

## 🔌 API Endpoints Reference

### **Core Scanning Endpoints**

```
POST /analyze
────────────────────────────────────────────────
Submit a new security scan (synchronous)

Request Body:
{
  "repo_url": "https://github.com/user/repo",
  "branch": "main" (optional),
  "analyzers": ["semgrep", "bandit", "depcheck"] (optional)
}

Response: 202 Accepted
{
  "job_id": "6caf9b01-b0f4-4e34-a78a-b4f4cc19965a",
  "status": "queued",
  "message": "Analysis job submitted successfully"
}
────────────────────────────────────────────────

POST /analyze-async
────────────────────────────────────────────────
Submit a scan with async processing (for webhooks)
Same as above, but with webhook_url in request
────────────────────────────────────────────────

GET /reports/{job_id}
────────────────────────────────────────────────
Get complete report for a specific job

Response: 200 OK
{
  "job_id": "6caf9b01...",
  "status": "completed",
  "repo_info": {
    "url": "https://github.com/user/repo",
    "branch": "main"
  },
  "issues": [
    {
      "file": "auth.py",
      "line": 45,
      "severity": "high",
      "rule": "B608",
      "message": "Possible SQL injection...",
      "analyzer": "bandit"
    }
  ],
  "severity_summary": {
    "critical": 0,
    "high": 3,
    "medium": 13,
    "low": 0,
    "total": 16
  },
  "ai_analysis": {
    "fixes": [...],
    "fixes_by_severity": {...},
    "recommendations_by_priority": {...}
  }
}
────────────────────────────────────────────────

GET /reports
────────────────────────────────────────────────
List all scan reports (paginated)

Query Params:
- limit: int (default 50)
- offset: int (default 0)
- status: "completed" | "failed" | "running" (optional)

Response: 200 OK
{
  "reports": [
    {
      "job_id": "6caf9b01...",
      "status": "completed",
      "submitted_at": "2025-10-31T10:30:00Z",
      "severity_summary": {...}
    }
  ],
  "total": 150,
  "limit": 50,
  "offset": 0
}
────────────────────────────────────────────────
```

### **AI Enhancement Endpoints**

```
POST /reports/{job_id}/enhance
────────────────────────────────────────────────
Trigger AI analysis for a completed scan

Response: 200 OK
{
  "job_id": "6caf9b01...",
  "ai_analysis": {
    "status": "completed",
    "fixes": [...],
    "fixes_by_severity": {
      "critical": [],
      "high": [fix1, fix2, fix3],
      "medium": [fix4...fix16],
      "low": []
    },
    "severity_summary": {
      "critical": 0,
      "high": 3,
      "medium": 13,
      "low": 0,
      "total": 16
    },
    "recommendations": [
      {
        "title": "Avoid using eval()",
        "description": "Never use eval()...",
        "priority": "high"
      }
    ],
    "recommendations_by_priority": {
      "high": [rec1...rec8],
      "medium": [rec9...rec15],
      "low": [rec16, rec17]
    }
  }
}

Auto-triggered: After scan completion if issues found
────────────────────────────────────────────────

GET /reports/{job_id}/enhanced
────────────────────────────────────────────────
Check if AI analysis exists for a job

Response: 200 OK
{
  "has_ai_analysis": true,
  "ai_analysis": {...}
}
────────────────────────────────────────────────
```

### **Utility Endpoints**

```
GET /health
────────────────────────────────────────────────
Health check endpoint

Response: 200 OK
{
  "status": "healthy",
  "version": "0.1.0",
  "active_jobs": 2,
  "ai_enabled": true
}
────────────────────────────────────────────────

GET /tools
────────────────────────────────────────────────
List available security analyzers

Response: 200 OK
{
  "tools": [
    {
      "name": "semgrep",
      "version": "1.45.0",
      "supported_languages": ["python", "javascript", "java", "go"]
    },
    {
      "name": "bandit",
      "version": "1.7.5",
      "supported_languages": ["python"]
    }
  ]
}
────────────────────────────────────────────────
```

---

## 📊 Data Flow Diagram

```
┌──────────────┐
│   USER       │
│  (Browser)   │
└──────┬───────┘
       │ 1. Submit scan: POST /analyze
       │    {repo_url, analyzers}
       ▼
┌──────────────────────────────────────────┐
│     FASTAPI BACKEND (Port 8000)          │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  Job Orchestrator                  │ │
│  │  • Generate job_id                 │ │
│  │  • Create JobInfo                  │ │
│  │  • Add to queue                    │ │
│  └────────────┬───────────────────────┘ │
│               │                          │
│               │ 2. Start background job  │
│               ▼                          │
│  ┌────────────────────────────────────┐ │
│  │  Repository Fetcher                │ │
│  │  • Clone repo to workspace         │ │
│  │  • Workspace: /storage/workspace/  │ │
│  └────────────┬───────────────────────┘ │
│               │                          │
│               │ 3. Workspace ready       │
│               ▼                          │
│  ┌────────────────────────────────────┐ │
│  │  Analyzer Registry                 │ │
│  │  • Detect applicable analyzers     │ │
│  │  • Run in parallel (ThreadPool)    │ │
│  │                                    │ │
│  │  ┌──────────┐  ┌──────────┐      │ │
│  │  │ Semgrep  │  │  Bandit  │      │ │
│  │  │          │  │          │      │ │
│  │  │ OWASP    │  │ Python   │      │ │
│  │  │ Rules    │  │ Security │      │ │
│  │  └────┬─────┘  └────┬─────┘      │ │
│  │       │             │             │ │
│  │       │ 4. Issues   │ 4. Issues   │ │
│  │       ▼             ▼             │ │
│  │  ┌──────────────────────────────┐│ │
│  │  │  Report Builder              ││ │
│  │  │  • Merge results             ││ │
│  │  │  • Deduplicate               ││ │
│  │  │  • Calculate severity_summary││ │
│  │  └────────┬─────────────────────┘│ │
│  └───────────┼───────────────────────┘ │
│              │                          │
│              │ 5. Base report complete  │
│              ▼                          │
│  ┌────────────────────────────────────┐ │
│  │  Storage: Save base report         │ │
│  │  /storage/reports/{job_id}.json    │ │
│  └────────────┬───────────────────────┘ │
│               │                          │
│               │ 6. Auto-trigger if issues│
│               ▼                          │
│  ┌────────────────────────────────────┐ │
│  │  CamelBridge / SimpleAIAnalyzer    │ │
│  │  • Load base report                │ │
│  │  • Sort issues by severity         │ │
│  │  • Call OpenAI API                 │ │
│  │  • Generate fixes + recommendations│ │
│  └────────────┬───────────────────────┘ │
│               │                          │
│               │ 7. AI response           │
│               ▼                          │
│  ┌────────────────────────────────────┐ │
│  │  Response Processing (app.py)      │ │
│  │  • Group fixes by severity         │ │
│  │  • Group recommendations by priority│ │
│  │  • Calculate severity_summary      │ │
│  │  • Merge with base report          │ │
│  └────────────┬───────────────────────┘ │
│               │                          │
│               │ 8. Update report         │
│               ▼                          │
│  ┌────────────────────────────────────┐ │
│  │  Storage: Update enhanced report   │ │
│  │  /storage/reports/{job_id}.json    │ │
│  │  + ai_analysis field               │ │
│  └────────────────────────────────────┘ │
└──────────────┬───────────────────────────┘
               │
               │ 9. Frontend polls: GET /reports/{job_id}
               ▼
┌──────────────────────────────────────────┐
│   NEXT.JS FRONTEND (Port 3000)           │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  API Client (lib/api-client.ts)    │ │
│  │  • Fetch enhanced report           │ │
│  │  • TypeScript interfaces validated │ │
│  └────────────┬───────────────────────┘ │
│               │                          │
│               │ 10. Render components    │
│               ▼                          │
│  ┌────────────────────────────────────┐ │
│  │  Report Display                    │ │
│  │  • Summary section                 │ │
│  │  • Fixes grouped by severity       │ │
│  │  • Recommendations by priority     │ │
│  └────────────┬───────────────────────┘ │
│               │                          │
│               │ 11. User clicks export   │
│               ▼                          │
│  ┌────────────────────────────────────┐ │
│  │  Export Utils (lib/export-utils.ts)│ │
│  │  • HTML: Styled with colors        │ │
│  │  • Markdown: Emoji indicators      │ │
│  │  • CSV: Priority columns           │ │
│  │  • JSON: Full nested structure     │ │
│  └────────────┬───────────────────────┘ │
└───────────────┼───────────────────────────┘
                │
                │ 12. Download file
                ▼
        ┌───────────────┐
        │  USER'S DISK  │
        │  report.html  │
        │  report.md    │
        │  report.csv   │
        └───────────────┘
```

---

## 🎯 Key Features Implemented

### ✅ **Current State (October 31, 2025)**

1. **All Severity Analysis**
   - Backend analyzes Critical, High, Medium, Low vulnerabilities
   - Previously filtered only High/Critical
   - Now processes all levels with proper grouping

2. **Severity-Based Grouping**
   - Fixes grouped: `fixes_by_severity.{critical, high, medium, low}`
   - Recommendations grouped: `recommendations_by_priority.{high, medium, low}`
   - Visual indicators with color coding (🔴🟡⚪)

3. **Enhanced TypeScript Types**
   - Frontend types match backend JSON structure
   - Full type safety across API client and export utilities
   - Proper object property access (title, description, priority)

4. **Export Functionality**
   - HTML: Professional styling with color-coded sections
   - Markdown: Priority headings with emoji indicators
   - CSV: Sortable with Priority column
   - JSON: Complete nested structure preserved

5. **Auto-Trigger AI Enhancement**
   - Automatically runs after scan completion
   - Only triggers if issues found
   - Background processing with progress updates

---

## 🔧 Configuration Files

### **Backend Environment** (`.env`)
```bash
# OpenAI API (Required for AI enhancement)
OPENAI_API_KEY=sk-proj-...

# Model Configuration
AI_MODEL=gpt-4
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=4000

# Storage
STORAGE_BASE=./storage

# Server
PORT=8000
HOST=0.0.0.0

# CORS (Frontend origins)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Job Processing
MAX_CONCURRENT_JOBS=2
MAX_UPLOAD_SIZE=52428800  # 50MB
```

### **Frontend Environment** (`.env.local`)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### **Docker Compose** (`docker-compose.yml`)
```yaml
version: '3.8'

services:
  scanner-backend:
    build:
      context: ./codeagent-scanner
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - AI_MODEL=gpt-4
    volumes:
      - ./storage:/app/storage

  scanner-frontend:
    build:
      context: ./codeagent-scanner-ui
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - scanner-backend
```

---

## 📝 Usage Example

### **Complete Workflow Example**

```bash
# Terminal 1: Start Backend
cd codeagent-scanner
docker build -t scanner-backend .
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=sk-proj-... \
  scanner-backend

# Terminal 2: Start Frontend
cd codeagent-scanner-ui
npm install
npm run dev

# Browser: http://localhost:3000
# 1. Enter repo: https://github.com/vulnerable-app/demo
# 2. Click "Start Scan"
# 3. Wait for completion (auto-redirects to results)
# 4. View grouped fixes and recommendations
# 5. Download report in desired format

# Terminal 3: API Testing
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/user/repo",
    "analyzers": ["semgrep", "bandit"]
  }'

# Response:
# {
#   "job_id": "6caf9b01-b0f4-4e34-a78a-b4f4cc19965a",
#   "status": "queued"
# }

# Check status:
curl http://localhost:8000/reports/6caf9b01-b0f4-4e34-a78a-b4f4cc19965a

# Trigger AI enhancement manually (optional, auto-runs):
curl -X POST http://localhost:8000/reports/6caf9b01-b0f4-4e34-a78a-b4f4cc19965a/enhance
```

---

## 🚀 Future Enhancements

1. **Real-time Collaboration**
   - Multi-user support
   - Shared scan results
   - Team annotations

2. **Advanced Filtering**
   - Filter by severity in UI
   - Search within fixes
   - Custom rule configuration

3. **CI/CD Integration**
   - GitHub Actions workflow
   - GitLab CI pipeline
   - Pull request comments

4. **Historical Tracking**
   - Trend analysis over time
   - Compare scans across commits
   - Security score dashboard

---

## 📚 Documentation

- `ALL_SEVERITY_ANALYSIS.md` - Backend implementation details
- `GROUPED_REPORT_STRUCTURE.md` - Complete user guide with examples
- `GROUPED_RECOMMENDATIONS_FIX.md` - Frontend fix documentation
- `API_DOCUMENTATION.md` - Complete API reference
- `DOCKER_GUIDE.md` - Container deployment guide

---

**Version:** 2.0  
**Last Updated:** October 31, 2025  
**Status:** ✅ Production Ready  
**Contributors:** Development Team
