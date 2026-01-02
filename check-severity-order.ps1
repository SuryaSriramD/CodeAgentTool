$data = Get-Content "D:\MinorProject\test-enhanced.json" | ConvertFrom-Json
Write-Host "Total fixes:" $data.ai_analysis.fixes.Count
Write-Host ""
Write-Host "First 10 fixes (ordered by severity):"
Write-Host "======================================"
for($i=0; $i -lt [Math]::Min(10, $data.ai_analysis.fixes.Count); $i++) {
    $fix = $data.ai_analysis.fixes[$i]
    $fileName = $fix.file.Split('/')[-1]
    Write-Host "$($i+1). Severity: $($fix.severity.PadRight(8)) | File: $fileName"
}
Write-Host ""
Write-Host "Severity summary:"
$severityCounts = @{}
foreach ($fix in $data.ai_analysis.fixes) {
    if (-not $severityCounts.ContainsKey($fix.severity)) {
        $severityCounts[$fix.severity] = 0
    }
    $severityCounts[$fix.severity]++
}
foreach ($key in $severityCounts.Keys | Sort-Object) {
    Write-Host "  $key`: $($severityCounts[$key])"
}
