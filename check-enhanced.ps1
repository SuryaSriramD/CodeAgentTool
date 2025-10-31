# Simple Enhanced Report Checker
param([string]$jobId = "")

$apiBase = "http://localhost:8000"

if ($jobId -eq "") {
    Write-Host "Fetching recent reports..." -ForegroundColor Yellow
    $reports = Invoke-RestMethod -Uri "$apiBase/reports" -Method Get
    
    foreach ($report in $reports) {
        Write-Host "`nJob ID: $($report.job_id)" -ForegroundColor White
        Write-Host "  Status: $($report.status)"
        Write-Host "  High: $($report.summary.high) | Critical: $($report.summary.critical)"
    }
    
    Write-Host "`nTo check enhanced report: .\check-enhanced-report.ps1 <job_id>" -ForegroundColor Yellow
    exit
}

Write-Host "Checking job: $jobId" -ForegroundColor Cyan

# Check job status
$job = Invoke-RestMethod -Uri "$apiBase/jobs/$jobId" -Method Get
Write-Host "Status: $($job.status)" -ForegroundColor Green

# Try to get enhanced report
try {
    $enhanced = Invoke-RestMethod -Uri "$apiBase/reports/$jobId/enhanced" -Method Get
    Write-Host "`nEnhanced Report Found!" -ForegroundColor Green
    Write-Host "AI Model: $($enhanced.meta.ai_model_used)"
    Write-Host "Files Analyzed: $($enhanced.summary.total_files_analyzed)"
    Write-Host "Fixes Generated: $($enhanced.summary.fixes_generated)"
    
    $enhanced | ConvertTo-Json -Depth 100 | Out-File "enhanced-$jobId.json"
    Write-Host "`nSaved to: enhanced-$jobId.json" -ForegroundColor Yellow
} catch {
    Write-Host "`nEnhanced report not available yet." -ForegroundColor Yellow
    Write-Host "Check logs: docker logs codeagent-scanner-backend-dev -f" -ForegroundColor Gray
}
