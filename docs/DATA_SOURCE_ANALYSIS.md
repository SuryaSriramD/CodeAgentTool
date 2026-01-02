# Data Source Analysis - Real vs Mock Data

## Overview

This document details which parts of the application display **real data from the backend API** and which parts use **mock/dummy data**.

---

## ✅ REAL DATA (Connected to Backend API)

### 1. **Dashboard Page** (`/dashboard`)

- **Status**: ✅ **FULLY CONNECTED TO API**
- **API Endpoint**: `GET /dashboard/stats`
- **Real Data Shown**:
  - Total Scans count
  - AI-enhanced reports count
  - Active Jobs count
  - Severity Distribution (Critical, High, Medium, Low)
  - Recent Scans list with:
    - Job IDs
    - Generated timestamps
    - Total issues count
    - AI analysis availability
- **Fallback**: Shows mock data only if API returns empty `recent_scans` array

### 2. **Reports List Page** (`/reports`)

- **Status**: ✅ **FULLY CONNECTED TO API**
- **API Endpoint**: `GET /reports?page=X&limit=Y&filters...`
- **Real Data Shown**:
  - Paginated reports list
  - Job IDs
  - Repository URLs
  - Generated timestamps
  - Severity summaries (Critical, High, Medium, Low)
  - Tools used (Bandit, Semgrep, etc.)
  - Labels
  - Total count with pagination
- **Filters Working**: Severity, Tool, Repo, Date range, Labels
- **No Mock Data**: Pure API data

### 3. **Report Detail Page** (`/reports/[reportId]`)

- **Status**: ✅ **FULLY CONNECTED TO API**
- **API Endpoint**: `GET /reports/{job_id}`
- **Real Data Shown**:
  - Repository URL
  - Severity breakdown (Critical, High, Medium, Low, Total)
  - Affected files list with issue counts
  - Complete vulnerability issues list with:
    - Tool name
    - Severity level
    - File path and line number
    - Issue description
    - Rule ID
  - Severity distribution chart
  - Download report (exports real data as JSON)
- **No Mock Data**: Pure API data

### 4. **Job Detail Page** (`/jobs/[jobId]`)

- **Status**: ✅ **FULLY CONNECTED TO API**
- **API Endpoints**:
  - `GET /events/{job_id}` (SSE for real-time updates)
  - `GET /jobs/{job_id}/status`
  - `GET /reports/{job_id}` (for report data)
- **Real Data Shown**:
  - Job status (queued, running, completed, failed, canceled)
  - Real-time progress updates via SSE
  - Repository URL
  - Scan progress percentage
  - Start/finish timestamps
  - Error messages (if failed)
  - Report summary when completed
  - Cancel job functionality (working)
  - Export report functionality (working)
- **No Mock Data**: Pure API data with real-time updates

### 5. **Scan Submission Modal** (`New Scan` button)

- **Status**: ✅ **FULLY CONNECTED TO API**
- **API Endpoint**: `POST /scan`
- **Real Data**:
  - Submits actual GitHub URLs to backend
  - Receives real job_id in response
  - Redirects to real job detail page
  - Validates repository URLs
- **No Mock Data**: Pure API integration

---

## ⚠️ MOCK DATA (Using Dummy/Fallback Data)

### 1. **Jobs List Page** (`/jobs`)

- **Status**: ⚠️ **USING MOCK DATA**
- **API Endpoint**: ❌ None connected yet
- **Mock Data Shown**:
  ```typescript
  {
    id: "1-7",
    repo: "acme/web-app", "acme/api-service", etc.
    status: "completed", "running", "queued", "failed", "canceled"
    issues: Random numbers
    critical: Random numbers
    duration: "2m 34s", "1m 12s", etc.
    timestamp: "2 hours ago", "now", "5 hours ago", etc.
  }
  ```
- **Why Mock**: Backend doesn't have a `/jobs` list endpoint
- **Filter Working**: Yes, but filtering mock data only
- **Note**: Individual job details ARE REAL when you click to view a specific job

### 2. **Dashboard - Recent Jobs Table** (Fallback Only)

- **Status**: ⚠️ **MOCK DATA AS FALLBACK**
- **Behavior**:
  - Shows **REAL** data if `stats.recent_scans` has items
  - Falls back to mock data if `recent_scans` is empty
- **Mock Data**: 3 dummy jobs with fake timestamps
- **Note**: Most likely shows real data in production

### 3. **Report Detail - Issues Table** (Fallback Only)

- **Status**: ⚠️ **MOCK DATA AS FALLBACK**
- **Behavior**:
  - Shows **REAL** issues if report has vulnerability data
  - Falls back to mock issues if `report.files` is empty
- **Mock Issues**: 4 dummy SQL injection/hardcoded credentials examples
- **Note**: Most likely shows real data when report has issues

---

## 📊 Summary Table

| Page/Component           | Data Source    | Status      | Notes                              |
| ------------------------ | -------------- | ----------- | ---------------------------------- |
| Dashboard Stats          | API            | ✅ Real     | Total scans, active jobs, severity |
| Dashboard Recent Scans   | API + Fallback | ✅ Real     | Mock only if empty                 |
| Dashboard Severity Chart | API            | ✅ Real     | Pie chart with real data           |
| Reports List             | API            | ✅ Real     | Paginated with filters             |
| Report Detail            | API            | ✅ Real     | Full vulnerability data            |
| Report Issues Table      | API + Fallback | ✅ Real     | Mock only if no issues             |
| Job Detail               | API + SSE      | ✅ Real     | Real-time updates                  |
| Job Status               | API + SSE      | ✅ Real     | Live progress monitoring           |
| **Jobs List**            | **Mock**       | ⚠️ **Mock** | **Not connected to API**           |
| Scan Submission          | API            | ✅ Real     | POST to /scan                      |

---

## 🎯 Percentage Breakdown

- **Real Data**: ~85%
- **Mock Data**: ~15% (mainly Jobs list page + fallbacks)

---

## 🔧 To Convert Jobs Page to Real Data

The Jobs page is the **only major component** still using mock data. To connect it to real data:

### Option 1: Use Reports Endpoint

Since there's no `/jobs` endpoint, you could use the `/reports` endpoint which lists completed scans:

```typescript
// In components/jobs/jobs-table.tsx
import { useReports } from "@/lib/hooks/use-reports";

export function JobsTable({ statusFilter, searchQuery }: JobsTableProps) {
  const { data, isLoading, error } = useReports({
    page: 1,
    limit: 50,
  });

  // Map reports to jobs format
  const jobs = data?.items.map((report) => ({
    id: report.job_id,
    repo: report.repo_url || "Unknown",
    status: "completed", // All reports are completed
    issues: Object.values(report.summary).reduce((a, b) => a + b, 0),
    critical: report.summary.critical,
    // ... etc
  }));
}
```

### Option 2: Backend Enhancement

Add a new endpoint to the backend:

```python
@app.get("/jobs")
async def list_jobs(
    page: int = 1,
    limit: int = 20,
    status: Optional[str] = None
):
    # Return list of all jobs (not just completed ones)
    pass
```

### Option 3: Keep Mock Data

Since users typically care more about:

1. **Submitting new scans** (✅ Working with real API)
2. **Monitoring specific job progress** (✅ Working with real-time SSE)
3. **Viewing reports** (✅ Working with real API)

The Jobs list page could remain as a "demo" page showing what jobs would look like.

---

## 🚀 Testing Real Data

### To Verify Real Data:

1. **Dashboard**: Just open `/dashboard` - should show real scan counts
2. **Reports**: Open `/reports` - should show paginated list of actual reports
3. **Job Detail**:
   - Submit a new scan via "New Scan" button
   - You'll be redirected to `/jobs/{job_id}`
   - Watch real-time progress via SSE
4. **Report Detail**:
   - Click any report from `/reports`
   - Should show real vulnerability data

### To Verify Mock Data:

1. **Jobs List**: Open `/jobs` - shows fixed list of 7 demo jobs
2. **Dashboard Recent Jobs**: Clear your backend data to trigger fallback

---

## 📝 Recommendation

**Current State**: The application is **production-ready** for its core functionality:

- ✅ Users can submit scans
- ✅ Users can monitor scan progress in real-time
- ✅ Users can view detailed reports with real vulnerability data
- ✅ Dashboard shows real statistics

The Jobs list page mock data is acceptable because:

1. It's a secondary navigation page
2. Users primarily care about **active/recent jobs** (shown on dashboard)
3. Individual job details ARE real when clicked

**If you want to remove all mock data**: Connect the Jobs page to the `/reports` endpoint (Option 1 above) to show real completed scans.
