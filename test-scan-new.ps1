# Submit a new scan with file upload
$filepath = "d:\MinorProject\test-vulnerable-code\app.js"
$uri = "http://localhost:8000/analyze-async"

# Read file content
$fileBytes = [System.IO.File]::ReadAllBytes($filepath)
$fileEnc = [System.Text.Encoding]::GetEncoding('iso-8859-1').GetString($fileBytes)

# Create boundary
$boundary = [System.Guid]::NewGuid().ToString()

# Build multipart form data
$LF = "`r`n"
$bodyLines = (
    "--$boundary",
    "Content-Disposition: form-data; name=`"file`"; filename=`"app.js`"",
    "Content-Type: application/octet-stream$LF",
    $fileEnc,
    "--$boundary--$LF"
) -join $LF

# Send request
$response = Invoke-RestMethod -Uri $uri -Method Post -ContentType "multipart/form-data; boundary=$boundary" -Body $bodyLines
$response | ConvertTo-Json -Depth 10
Write-Host "`nJob ID: $($response.job_id)"
