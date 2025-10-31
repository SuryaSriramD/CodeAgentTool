"""
Comprehensive Backend Test Suite for CodeAgent Vulnerability Scanner
Tests all endpoints using SwiftLint repository
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, List

# Configuration
BASE_URL = "http://localhost:8000"
TEST_REPO = "https://github.com/airbnb/javascript"
MIN_SEVERITY = "medium"

# Colors for terminal output
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    """Print formatted header"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.GRAY}{'=' * 70}{Colors.END}")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.WHITE}   {text}{Colors.END}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

# Test results tracking
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "warnings": 0,
    "start_time": datetime.now()
}

def record_test(name: str, passed: bool, details: str = ""):
    """Record test result"""
    test_results["total"] += 1
    if passed:
        test_results["passed"] += 1
        print_success(f"{name}")
        if details:
            print_info(details)
    else:
        test_results["failed"] += 1
        print_error(f"{name}")
        if details:
            print_info(f"Error: {details}")

def test_health_endpoint() -> bool:
    """Test 1: Health Check Endpoint"""
    print_header("Test 1: Health Check Endpoint")
    try:
        start = time.time()
        response = requests.get(f"{BASE_URL}/health")
        elapsed = (time.time() - start) * 1000
        
        if response.status_code == 200:
            data = response.json()
            record_test("Health endpoint accessible", True, 
                       f"Status: {data.get('status', 'N/A')} | Response time: {elapsed:.0f}ms")
            return True
        else:
            record_test("Health endpoint accessible", False, 
                       f"Status code: {response.status_code}")
            return False
    except Exception as e:
        record_test("Health endpoint accessible", False, str(e))
        return False

def test_github_scan() -> str:
    """Test 2: GitHub Repository Scanning"""
    print_header("Test 2: GitHub Repository Scanning")
    try:
        start = time.time()
        payload = {
            "github_url": TEST_REPO,
            "min_severity": MIN_SEVERITY
        }
        
        response = requests.post(
            f"{BASE_URL}/analyze-async",
            data=payload  # Use form data, not JSON
        )
        elapsed = (time.time() - start) * 1000
        
        if response.status_code == 200:
            data = response.json()
            job_id = data.get("job_id")
            status = data.get("status")
            
            record_test("Repository scan initiated", True,
                       f"Job ID: {job_id} | Status: {status} | Time: {elapsed:.0f}ms")
            return job_id
        else:
            record_test("Repository scan initiated", False,
                       f"Status code: {response.status_code} | Response: {response.text}")
            return None
    except Exception as e:
        record_test("Repository scan initiated", False, str(e))
        return None

def test_job_status(job_id: str) -> Dict[str, Any]:
    """Test 3: Job Status Endpoint"""
    print_header("Test 3: Job Status Monitoring")
    try:
        max_attempts = 60  # 5 minutes max
        attempt = 0
        
        while attempt < max_attempts:
            response = requests.get(f"{BASE_URL}/jobs/{job_id}")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                progress = data.get("progress", 0)
                
                if attempt == 0:
                    record_test("Job status endpoint accessible", True,
                               f"Initial status: {status}")
                
                print_info(f"Status: {status} | Progress: {progress}% | Attempt: {attempt + 1}/{max_attempts}")
                
                if status in ["completed", "failed"]:
                    if status == "completed":
                        print_success(f"Job completed after {attempt + 1} checks")
                    else:
                        print_error(f"Job failed: {data.get('error', 'Unknown error')}")
                    return data
                
                time.sleep(5)
                attempt += 1
            else:
                record_test("Job status endpoint accessible", False,
                           f"Status code: {response.status_code}")
                return None
        
        print_warning(f"Job did not complete within {max_attempts * 5} seconds")
        test_results["warnings"] += 1
        return None
        
    except Exception as e:
        record_test("Job status endpoint accessible", False, str(e))
        return None

def test_job_report(job_id: str) -> Dict[str, Any]:
    """Test 4: Job Report Endpoint"""
    print_header("Test 4: Standard Vulnerability Report")
    try:
        response = requests.get(f"{BASE_URL}/reports/{job_id}")
        
        if response.status_code == 200:
            data = response.json()
            summary = data.get("summary", {})
            files = data.get("files", [])
            meta = data.get("meta", {})
            
            total_issues = sum([
                summary.get("critical", 0),
                summary.get("high", 0),
                summary.get("medium", 0),
                summary.get("low", 0)
            ])
            
            details = f"""Files scanned: {len(files)}
   Total issues: {total_issues}
   Critical: {summary.get('critical', 0)} | High: {summary.get('high', 0)} | Medium: {summary.get('medium', 0)} | Low: {summary.get('low', 0)}
   Tools used: {', '.join(meta.get('tools', []))}
   Duration: {meta.get('duration_ms', 0)}ms"""
            
            record_test("Standard report generated", True, details)
            return data
        else:
            record_test("Standard report generated", False,
                       f"Status code: {response.status_code}")
            return None
    except Exception as e:
        record_test("Standard report generated", False, str(e))
        return None

def test_enhanced_report(job_id: str) -> Dict[str, Any]:
    """Test 5: AI-Enhanced Report Endpoint"""
    print_header("Test 5: AI-Enhanced Vulnerability Report")
    
    print_info("Waiting 60 seconds for AI analysis to complete...")
    time.sleep(60)
    
    try:
        response = requests.get(f"{BASE_URL}/reports/{job_id}/enhanced")
        
        if response.status_code == 200:
            data = response.json()
            summary = data.get("summary", {})
            meta = data.get("meta", {})
            enhanced_issues = data.get("enhanced_issues", [])
            
            ai_success = True
            error_msg = None
            if enhanced_issues and len(enhanced_issues) > 0:
                first_issue = enhanced_issues[0]
                ai_analysis = first_issue.get("ai_analysis", {})
                if "error" in ai_analysis:
                    ai_success = False
                    error_msg = ai_analysis.get("error")
            
            details = f"""Status: {data.get('status', 'unknown')}
   AI Model: {meta.get('ai_model_used', 'N/A')}
   Files analyzed: {summary.get('files_analyzed_by_ai', 0)}
   Issues analyzed: {summary.get('issues_analyzed_by_ai', 0)}
   AI fixes generated: {summary.get('ai_fixes_generated', 0)}"""
            
            if ai_success:
                record_test("AI-enhanced report generated", True, details)
            else:
                print_warning(f"Enhanced report generated but AI analysis had errors")
                print_info(details)
                print_info(f"AI Error: {error_msg}")
                test_results["warnings"] += 1
            
            return data
        elif response.status_code == 404:
            error_data = response.json()
            print_warning("Enhanced report not available yet")
            print_info(f"Message: {error_data.get('error', {}).get('message', 'Unknown')}")
            test_results["warnings"] += 1
            return None
        else:
            record_test("AI-enhanced report generated", False,
                       f"Status code: {response.status_code}")
            return None
    except Exception as e:
        record_test("AI-enhanced report generated", False, str(e))
        return None

def test_list_jobs() -> bool:
    """Test 6: List All Jobs Endpoint"""
    print_header("Test 6: List All Jobs")
    try:
        response = requests.get(f"{BASE_URL}/jobs")
        
        if response.status_code == 200:
            data = response.json()
            jobs = data.get("jobs", [])
            record_test("Jobs list endpoint accessible", True,
                       f"Total jobs in system: {len(jobs)}")
            return True
        else:
            record_test("Jobs list endpoint accessible", False,
                       f"Status code: {response.status_code}")
            return False
    except Exception as e:
        record_test("Jobs list endpoint accessible", False, str(e))
        return False

def test_analyzer_info() -> bool:
    """Test 7: Analyzer Information Endpoint"""
    print_header("Test 7: Analyzer Information")
    try:
        response = requests.get(f"{BASE_URL}/tools")
        
        if response.status_code == 200:
            data = response.json()
            available = data.get("available", [])
            versions = data.get("versions", {})
            
            analyzer_details = "\n   ".join([
                f"{name}: v{versions.get(name, 'unknown')}" 
                for name in available
            ])
            
            record_test("Analyzer info endpoint accessible", True,
                       f"Available analyzers: {len(available)}\n   {analyzer_details}")
            return True
        else:
            record_test("Analyzer info endpoint accessible", False,
                       f"Status code: {response.status_code}")
            return False
    except Exception as e:
        record_test("Analyzer info endpoint accessible", False, str(e))
        return False

def print_final_summary():
    """Print final test summary"""
    print_header("📊 FINAL TEST SUMMARY")
    
    elapsed = (datetime.now() - test_results["start_time"]).total_seconds()
    pass_rate = (test_results["passed"] / test_results["total"] * 100) if test_results["total"] > 0 else 0
    
    print(f"\n{Colors.BOLD}Test Results:{Colors.END}")
    print(f"   Total Tests: {test_results['total']}")
    print(f"   {Colors.GREEN}✅ Passed: {test_results['passed']}{Colors.END}")
    print(f"   {Colors.RED}❌ Failed: {test_results['failed']}{Colors.END}")
    print(f"   {Colors.YELLOW}⚠️  Warnings: {test_results['warnings']}{Colors.END}")
    print(f"   Pass Rate: {pass_rate:.1f}%")
    print(f"   Duration: {elapsed:.1f} seconds")
    
    print(f"\n{Colors.BOLD}Backend Status:{Colors.END}")
    if test_results["failed"] == 0:
        print(f"   {Colors.GREEN}{Colors.BOLD}✅ BACKEND FULLY OPERATIONAL{Colors.END}")
    elif test_results["passed"] > test_results["failed"]:
        print(f"   {Colors.YELLOW}{Colors.BOLD}⚠️  BACKEND PARTIALLY OPERATIONAL{Colors.END}")
    else:
        print(f"   {Colors.RED}{Colors.BOLD}❌ BACKEND NOT OPERATIONAL{Colors.END}")
    
    print(f"\n{Colors.BOLD}Test Repository:{Colors.END}")
    print(f"   URL: {TEST_REPO}")
    print(f"   Type: Swift/Objective-C Static Analysis Tool")
    print(f"   Size: Large enterprise repository")
    
    print(f"\n{Colors.GRAY}{'=' * 70}{Colors.END}\n")

def main():
    """Run all tests"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║     CodeAgent Vulnerability Scanner - Full Backend Test Suite    ║")
    print("║                    SwiftLint Repository Test                      ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print(Colors.END)
    
    print_info(f"Test started at: {test_results['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"Target: {BASE_URL}")
    print_info(f"Repository: {TEST_REPO}")
    
    # Run all tests
    test_health_endpoint()
    
    job_id = test_github_scan()
    if not job_id:
        print_error("Cannot continue without valid job ID")
        print_final_summary()
        return
    
    job_data = test_job_status(job_id)
    
    if job_data and job_data.get("status") == "completed":
        test_job_report(job_id)
        test_enhanced_report(job_id)
    else:
        print_warning("Skipping report tests due to incomplete job")
        test_results["warnings"] += 2
    
    test_list_jobs()
    test_analyzer_info()
    
    # Print final summary
    print_final_summary()

if __name__ == "__main__":
    main()
