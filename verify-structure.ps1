$data = Get-Content "D:\MinorProject\test-enhanced-grouped.json" | ConvertFrom-Json

Write-Host "Available fields in ai_analysis:" -ForegroundColor Cyan
$data.ai_analysis | Get-Member -MemberType NoteProperty | Select-Object -ExpandProperty Name | ForEach-Object {
    Write-Host "  ✓ $_" -ForegroundColor Green
}

Write-Host ""
Write-Host "Sample fix from HIGH severity:" -ForegroundColor Cyan
$data.ai_analysis.fixes_by_severity.high[0] | Format-List

Write-Host "Sample recommendation from HIGH priority:" -ForegroundColor Cyan
$data.ai_analysis.recommendations_by_priority.high[0] | Format-List
