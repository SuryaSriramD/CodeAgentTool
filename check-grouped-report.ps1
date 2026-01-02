# Download the enhanced report
docker exec codeagent-scanner-backend sh -c "cat /app/storage/reports/6caf9b01-b0f4-4e34-a78a-b4f4cc19965a_enhanced.json" > D:\MinorProject\test-enhanced-grouped.json

# Parse and display grouped structure
$data = Get-Content "D:\MinorProject\test-enhanced-grouped.json" | ConvertFrom-Json

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   ENHANCED REPORT - GROUPED STRUCTURE" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Display severity summary
Write-Host "SEVERITY SUMMARY:" -ForegroundColor Yellow
Write-Host "  Critical: $($data.ai_analysis.severity_summary.critical)" -ForegroundColor Red
Write-Host "  High:     $($data.ai_analysis.severity_summary.high)" -ForegroundColor Magenta
Write-Host "  Medium:   $($data.ai_analysis.severity_summary.medium)" -ForegroundColor DarkYellow
Write-Host "  Low:      $($data.ai_analysis.severity_summary.low)" -ForegroundColor Gray
Write-Host "  TOTAL:    $($data.ai_analysis.severity_summary.total)" -ForegroundColor White
Write-Host ""

# Display fixes grouped by severity
Write-Host "FIXES BY SEVERITY:" -ForegroundColor Yellow
Write-Host ""

if ($data.ai_analysis.fixes_by_severity.critical.Count -gt 0) {
    Write-Host "  CRITICAL SEVERITY ($($data.ai_analysis.fixes_by_severity.critical.Count) fixes):" -ForegroundColor Red
    foreach ($fix in $data.ai_analysis.fixes_by_severity.critical) {
        $fileName = $fix.file.Split('/')[-1]
        Write-Host "    - $fileName`: $($fix.vulnerability_type)" -ForegroundColor Red
    }
    Write-Host ""
}

if ($data.ai_analysis.fixes_by_severity.high.Count -gt 0) {
    Write-Host "  HIGH SEVERITY ($($data.ai_analysis.fixes_by_severity.high.Count) fixes):" -ForegroundColor Magenta
    foreach ($fix in $data.ai_analysis.fixes_by_severity.high) {
        $fileName = $fix.file.Split('/')[-1]
        Write-Host "    - $fileName`: $($fix.vulnerability_type)" -ForegroundColor Magenta
    }
    Write-Host ""
}

if ($data.ai_analysis.fixes_by_severity.medium.Count -gt 0) {
    Write-Host "  MEDIUM SEVERITY ($($data.ai_analysis.fixes_by_severity.medium.Count) fixes):" -ForegroundColor DarkYellow
    foreach ($fix in $data.ai_analysis.fixes_by_severity.medium | Select-Object -First 5) {
        $fileName = $fix.file.Split('/')[-1]
        Write-Host "    - $fileName`: $($fix.vulnerability_type)" -ForegroundColor DarkYellow
    }
    if ($data.ai_analysis.fixes_by_severity.medium.Count -gt 5) {
        Write-Host "    ... and $($data.ai_analysis.fixes_by_severity.medium.Count - 5) more" -ForegroundColor Gray
    }
    Write-Host ""
}

if ($data.ai_analysis.fixes_by_severity.low.Count -gt 0) {
    Write-Host "  LOW SEVERITY ($($data.ai_analysis.fixes_by_severity.low.Count) fixes):" -ForegroundColor Gray
    foreach ($fix in $data.ai_analysis.fixes_by_severity.low | Select-Object -First 3) {
        $fileName = $fix.file.Split('/')[-1]
        Write-Host "    - $fileName`: $($fix.vulnerability_type)" -ForegroundColor Gray
    }
    Write-Host ""
}

# Display recommendations grouped by priority
Write-Host "RECOMMENDATIONS BY PRIORITY:" -ForegroundColor Yellow
Write-Host ""

if ($data.ai_analysis.recommendations_by_priority.high.Count -gt 0) {
    Write-Host "  HIGH PRIORITY ($($data.ai_analysis.recommendations_by_priority.high.Count) recommendations):" -ForegroundColor Red
    foreach ($rec in $data.ai_analysis.recommendations_by_priority.high) {
        Write-Host "    - $($rec.title)" -ForegroundColor Red
    }
    Write-Host ""
}

if ($data.ai_analysis.recommendations_by_priority.medium.Count -gt 0) {
    Write-Host "  MEDIUM PRIORITY ($($data.ai_analysis.recommendations_by_priority.medium.Count) recommendations):" -ForegroundColor DarkYellow
    foreach ($rec in $data.ai_analysis.recommendations_by_priority.medium) {
        Write-Host "    - $($rec.title)" -ForegroundColor DarkYellow
    }
    Write-Host ""
}

if ($data.ai_analysis.recommendations_by_priority.low.Count -gt 0) {
    Write-Host "  LOW PRIORITY ($($data.ai_analysis.recommendations_by_priority.low.Count) recommendations):" -ForegroundColor Gray
    foreach ($rec in $data.ai_analysis.recommendations_by_priority.low) {
        Write-Host "    - $($rec.title)" -ForegroundColor Gray
    }
    Write-Host ""
}

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Status: $($data.ai_analysis.status)" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
