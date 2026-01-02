# Enhanced Report Checker
# Usage: .\check-enhanced-report.ps1 [job_id]

param(
    [string]$jobId = ""
)

$apiBase = "http://localhost:8000"

if ($jobId -eq "") {
    Write-Host "No job ID provided. Fetching recent reports..." -ForegroundColor Yellow
    Write-Host ""
    
    # Get all reports
    try {
        $reports = Invoke-RestMethod -Uri "$apiBase/reports" -Method Get
        
        Write-Host "Recent Scan Reports:" -ForegroundColor Cyan
        Write-Host "===================" -ForegroundColor Cyan
        Write-Host ""
        
        foreach ($report in $reports) {
            $jobIdShort = $report.job_id.Substring(0, 8)
            $status = $report.status
            $highCount = if ($report.summary.high) { $report.summary.high } else { 0 }
            $criticalCount = if ($report.summary.critical) { $report.summary.critical } else { 0 }
            
            Write-Host "Job ID: $($report.job_id)" -ForegroundColor White
            Write-Host "  Status: $status" -ForegroundColor $(if ($status -eq "completed") { "Green" } else { "Yellow" })
            Write-Host "  Repo: $($report.repo_url)" -ForegroundColor Gray
            Write-Host "  High: $highCount | Critical: $criticalCount" -ForegroundColor $(if ($highCount -gt 0 -or $criticalCount -gt 0) { "Red" } else { "Gray" })
            Write-Host "  Timestamp: $($report.timestamp)" -ForegroundColor Gray
            
            # Check if enhanced report might exist
            if (($highCount -gt 0 -or $criticalCount -gt 0) -and $status -eq "completed") {
                Write-Host "  ✨ Eligible for AI Enhancement" -ForegroundColor Magenta
            }
            Write-Host ""
        }
        
        Write-Host ""
        Write-Host "To check a specific enhanced report, run:" -ForegroundColor Yellow
        Write-Host "  .\check-enhanced-report.ps1 <job_id>" -ForegroundColor White
        
    } catch {
        Write-Host "❌ Error fetching reports: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    exit
}

# Check specific job
Write-Host "Checking Enhanced Report for Job: $jobId" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check regular report first
Write-Host "[1/4] Fetching regular report..." -ForegroundColor Yellow
try {
    $job = Invoke-RestMethod -Uri "$apiBase/jobs/$jobId" -Method Get
    
    Write-Host "  ✅ Job Status: $($job.status)" -ForegroundColor Green
    Write-Host "  Repository: $($job.repo_url)" -ForegroundColor Gray
    Write-Host ""
    
    if ($job.status -ne "completed") {
        Write-Host "  ⚠️  Job not completed yet. Wait for completion before checking enhanced report." -ForegroundColor Yellow
        exit
    }
    
} catch {
    Write-Host "  ❌ Job not found: $jobId" -ForegroundColor Red
    exit
}

# 2. Check regular report for high/critical issues
Write-Host "[2/4] Checking vulnerability severity..." -ForegroundColor Yellow
try {
    $report = Invoke-RestMethod -Uri "$apiBase/reports/$jobId" -Method Get
    
    $highCount = if ($report.summary.high) { $report.summary.high } else { 0 }
    $criticalCount = if ($report.summary.critical) { $report.summary.critical } else { 0 }
    $mediumCount = if ($report.summary.medium) { $report.summary.medium } else { 0 }
    $lowCount = if ($report.summary.low) { $report.summary.low } else { 0 }
    
    Write-Host "  Critical: $criticalCount" -ForegroundColor Red
    Write-Host "  High: $highCount" -ForegroundColor Red
    Write-Host "  Medium: $mediumCount" -ForegroundColor Yellow
    Write-Host "  Low: $lowCount" -ForegroundColor Gray
    Write-Host ""
    
    if ($highCount -eq 0 -and $criticalCount -eq 0) {
    Write-Host "  [!] No high or critical issues found. AI analysis only runs for high/critical severity." -ForegroundColor Cyan
        Write-Host ""
        exit
    }
    
    Write-Host "  [OK] Qualifies for AI Enhancement ($highCount high, $criticalCount critical)" -ForegroundColor Green
    Write-Host ""
    
} catch {
    Write-Host "  ❌ Could not fetch report" -ForegroundColor Red
    exit
}

# 3. Check backend logs
Write-Host "[3/4] Checking backend logs for AI analysis..." -ForegroundColor Yellow
$logOutput = docker logs codeagent-scanner-backend-dev 2>&1 | Select-String -Pattern "AI analysis.*$jobId" | Select-Object -Last 5

if ($logOutput) {
    Write-Host "  ✅ AI analysis logs found:" -ForegroundColor Green
    foreach ($line in $logOutput) {
        Write-Host "    $line" -ForegroundColor Gray
    }
} else {
    Write-Host "  ⚠️  No AI analysis logs found. AI analysis may still be running or failed." -ForegroundColor Yellow
}
Write-Host ""

# 4. Try to fetch enhanced report
Write-Host "[4/4] Fetching AI-enhanced report..." -ForegroundColor Yellow
try {
    $enhanced = Invoke-RestMethod -Uri "$apiBase/reports/$jobId/enhanced" -Method Get
    
    Write-Host "  ✅ Enhanced Report Found!" -ForegroundColor Green
    Write-Host ""
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host "AI-ENHANCED REPORT SUMMARY" -ForegroundColor Cyan
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "Job ID: $($enhanced.job_id)" -ForegroundColor White
    Write-Host "Status: $($enhanced.status)" -ForegroundColor Green
    Write-Host "AI Model: $($enhanced.meta.ai_model_used)" -ForegroundColor Magenta
    Write-Host ""
    
    Write-Host "Enhanced Issues Analysis:" -ForegroundColor Yellow
    Write-Host "  Total Files Analyzed: $($enhanced.summary.total_files_analyzed)" -ForegroundColor White
    Write-Host "  Total Issues Analyzed: $($enhanced.summary.total_issues_analyzed)" -ForegroundColor White
    Write-Host "  Fixes Generated: $($enhanced.summary.fixes_generated)" -ForegroundColor White
    Write-Host ""
    
    # Show details of each enhanced issue
    $issueNum = 1
    foreach ($issue in $enhanced.enhanced_issues) {
        Write-Host "[$issueNum] File: $($issue.file)" -ForegroundColor Cyan
        Write-Host "    Issues Analyzed: $($issue.issues_analyzed)" -ForegroundColor White
        
        if ($issue.ai_analysis) {
            $analysis = $issue.ai_analysis
            
            if ($analysis.root_cause) {
                Write-Host "    Root Cause: $($analysis.root_cause)" -ForegroundColor Yellow
            }
            
            if ($analysis.security_impact) {
                Write-Host "    Security Impact: $($analysis.security_impact)" -ForegroundColor Red
            }
            
            if ($analysis.fix) {
                Write-Host "    ✨ Fix Available:" -ForegroundColor Green
                Write-Host "      Explanation: $($analysis.fix.explanation)" -ForegroundColor Gray
                Write-Host ""
                Write-Host "      Original Code:" -ForegroundColor Red
                Write-Host "      $($analysis.fix.original_code)" -ForegroundColor DarkRed
                Write-Host ""
                Write-Host "      Fixed Code:" -ForegroundColor Green
                Write-Host "      $($analysis.fix.fixed_code)" -ForegroundColor DarkGreen
            }
            
            if ($analysis.recommendations) {
                Write-Host "    📋 Recommendations:" -ForegroundColor Cyan
                foreach ($rec in $analysis.recommendations) {
                    Write-Host "      • $rec" -ForegroundColor White
                }
            }
            
            if ($analysis.confidence) {
                $confidencePercent = [math]::Round($analysis.confidence * 100, 1)
                Write-Host "    Confidence: $confidencePercent%" -ForegroundColor Magenta
            }
        }
        
        Write-Host ""
        $issueNum++
    }
    
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host "✅ AI-Enhanced Report Complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Full JSON saved to: enhanced-report-$jobId.json" -ForegroundColor Yellow
    
    # Save full JSON
    $enhanced | ConvertTo-Json -Depth 100 | Out-File "enhanced-report-$jobId.json" -Encoding utf8
    
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    
    if ($statusCode -eq 404) {
        Write-Host "  ⚠️  Enhanced report not available yet." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Possible reasons:" -ForegroundColor Cyan
        Write-Host "  1. AI analysis is still running (wait 1-2 minutes)" -ForegroundColor White
        Write-Host "  2. AI analysis failed (check logs above)" -ForegroundColor White
        Write-Host "  3. ENABLE_AI_ANALYSIS is disabled" -ForegroundColor White
        Write-Host ""
        Write-Host "Check configuration:" -ForegroundColor Yellow
        Write-Host "  curl http://localhost:8000/config/ai" -ForegroundColor White
        Write-Host ""
        Write-Host "Monitor logs:" -ForegroundColor Yellow
        Write-Host "  docker logs codeagent-scanner-backend-dev -f" -ForegroundColor White
    } else {
        Write-Host "  ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}
