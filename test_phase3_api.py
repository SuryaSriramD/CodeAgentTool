"""
Test script for Phase 3 API endpoints.
Run this after starting the FastAPI server to verify all endpoints work.
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_response(endpoint: str, response: requests.Response):
    """Print formatted response."""
    print(f"\n📍 {endpoint}")
    print(f"Status: {response.status_code}")
    try:
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def test_get_ai_config():
    """Test GET /config/ai endpoint."""
    print_section("Test 1: GET /config/ai")
    
    try:
        response = requests.get(f"{BASE_URL}/config/ai")
        print_response("GET /config/ai", response)
        
        if response.status_code == 200:
            data = response.json()
            assert "enabled" in data
            assert "model" in data
            assert "min_severity" in data
            print("\n✅ Test PASSED - All required fields present")
        else:
            print("\n❌ Test FAILED - Unexpected status code")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server. Is it running?")
        print("   Start with: python codeagent-scanner/api/app.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

def test_update_ai_config():
    """Test PATCH /config/ai endpoint."""
    print_section("Test 2: PATCH /config/ai")
    
    # Test 2.1: Valid update
    print("\n--- Test 2.1: Valid update ---")
    try:
        payload = {"min_severity": "critical"}
        response = requests.patch(
            f"{BASE_URL}/config/ai",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print_response("PATCH /config/ai (valid)", response)
        
        if response.status_code == 200:
            data = response.json()
            assert data["ok"] == True
            assert "critical" in str(data["updated"])
            print("\n✅ Test 2.1 PASSED - Config updated successfully")
        else:
            print("\n❌ Test 2.1 FAILED")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
    
    # Test 2.2: Invalid model
    print("\n--- Test 2.2: Invalid model (should fail) ---")
    try:
        payload = {"model": "INVALID_MODEL"}
        response = requests.patch(
            f"{BASE_URL}/config/ai",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print_response("PATCH /config/ai (invalid)", response)
        
        if response.status_code == 400:
            print("\n✅ Test 2.2 PASSED - Validation working correctly")
        else:
            print("\n❌ Test 2.2 FAILED - Should have rejected invalid model")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
    
    # Test 2.3: Multiple updates
    print("\n--- Test 2.3: Multiple field update ---")
    try:
        payload = {
            "model": "GPT_3_5_TURBO",
            "min_severity": "high",
            "max_concurrent_reviews": 2
        }
        response = requests.patch(
            f"{BASE_URL}/config/ai",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print_response("PATCH /config/ai (multiple)", response)
        
        if response.status_code == 200:
            data = response.json()
            assert len(data["updated"]) == 3
            print("\n✅ Test 2.3 PASSED - Multiple fields updated")
        else:
            print("\n❌ Test 2.3 FAILED")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

def test_dashboard_stats():
    """Test GET /dashboard/stats endpoint."""
    print_section("Test 3: GET /dashboard/stats")
    
    try:
        response = requests.get(f"{BASE_URL}/dashboard/stats")
        print_response("GET /dashboard/stats", response)
        
        if response.status_code == 200:
            data = response.json()
            assert "total_scans" in data
            assert "ai_enhanced_reports" in data
            assert "severity_distribution" in data
            assert "active_jobs" in data
            assert "recent_scans" in data
            print("\n✅ Test PASSED - All required fields present")
            
            # Print summary
            print("\n📊 Dashboard Summary:")
            print(f"   Total Scans: {data['total_scans']}")
            print(f"   AI Enhanced: {data['ai_enhanced_reports']}")
            print(f"   Active Jobs: {data['active_jobs']}")
            print(f"   Severity Distribution:")
            for severity, count in data['severity_distribution'].items():
                print(f"     {severity.capitalize()}: {count}")
        else:
            print("\n❌ Test FAILED")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

def test_health_check():
    """Test health endpoint (should already exist)."""
    print_section("Test 0: Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print_response("GET /health", response)
        
        if response.status_code == 200:
            print("\n✅ Server is healthy and running")
        else:
            print("\n⚠️  Server health check returned unexpected status")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

def run_all_tests():
    """Run all API tests."""
    print("\n")
    print("╔" + "═"*58 + "╗")
    print("║" + " "*15 + "PHASE 3 API ENDPOINT TESTS" + " "*16 + "║")
    print("╚" + "═"*58 + "╝")
    
    # Test server health first
    test_health_check()
    
    # Test Phase 3 endpoints
    test_get_ai_config()
    test_update_ai_config()
    test_dashboard_stats()
    
    # Summary
    print_section("Test Summary")
    print("\n✅ If all tests passed, Phase 3 implementation is working!")
    print("⚠️  If any tests failed, check the server logs for details.")
    print("\nTo start the server:")
    print("  cd codeagent-scanner/api")
    print("  python app.py")
    print("\n")

if __name__ == "__main__":
    run_all_tests()
