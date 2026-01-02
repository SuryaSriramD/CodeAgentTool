$body = @{
    repo_url = "file://D:/MinorProject/test-vulnerable-code"
    analyzers = @("semgrep", "bandit")
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/analyze-async" -Method Post -Body $body -ContentType "application/json"
$response | ConvertTo-Json -Depth 10
Write-Host "`nJob ID: $($response.job_id)"
