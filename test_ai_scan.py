import requests
import json
import time

# Upload file for scanning
print('Uploading file for scanning...')
with open('d:/MinorProject/test_scan.zip', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/analyze', files=files)
    
result = response.json()
print('Scan initiated!')
print(json.dumps(result, indent=2))

job_id = result['job_id']
print(f'\nJob ID: {job_id}')

# Wait for scan to complete
print('\nWaiting for scan to complete...')
for i in range(30):
    time.sleep(2)
    status_response = requests.get(f'http://localhost:8000/jobs/{job_id}')
    status = status_response.json()
    print(f'Status: {status.get("status", "unknown")}')
    
    if status['status'] in ['completed', 'failed']:
        break

# Get the enhanced report
print('\nRequesting enhanced report with AI analysis...')
enhanced_response = requests.get(f'http://localhost:8000/reports/{job_id}/enhanced')
if enhanced_response.status_code == 200:
    enhanced_report = enhanced_response.json()
    print('\n AI ENHANCEMENT SUCCESSFUL!')
    print(json.dumps(enhanced_report, indent=2))
else:
    print(f'\n Enhanced report not ready: {enhanced_response.status_code}')
    print(enhanced_response.text)
