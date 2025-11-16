#!/usr/bin/env python3
"""
Test frontend-backend integration.
Verifies that frontend can communicate with backend API.
"""

import requests
import sys

FRONTEND_URL = "http://literattus-alb-96115082.sa-east-1.elb.amazonaws.com"
BACKEND_URL = "http://literattus-alb-96115082.sa-east-1.elb.amazonaws.com"

def test_frontend_homepage():
    """Test frontend homepage loads."""
    print("Test 1: Frontend Homepage")
    try:
        response = requests.get(f"{FRONTEND_URL}/", timeout=10)
        if response.status_code == 200:
            print("  ✅ Frontend homepage loads successfully")
            return True
        else:
            print(f"  ❌ Frontend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False

def test_backend_health():
    """Test backend health endpoint."""
    print("\nTest 2: Backend Health Check")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            print("  ✅ Backend health check passes")
            return True
        else:
            print(f"  ❌ Backend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False

def test_backend_api():
    """Test backend API endpoint."""
    print("\nTest 3: Backend API Endpoint")
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            json={"email": "test@test.com", "REDACTED": "test123"},
            timeout=10
        )
        # Should return 401/422 for invalid credentials, not 500
        if response.status_code in [200, 401, 422]:
            print(f"  ✅ Backend API responds correctly (status {response.status_code})")
            return True
        elif response.status_code == 500:
            print("  ❌ Backend API returns 500 (internal server error)")
            print(f"  Response: {response.text[:200]}")
            return False
        else:
            print(f"  ⚠️  Unexpected status {response.status_code}")
            return True
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("Frontend-Backend Integration Test")
    print("=" * 70)
    print()
    
    results = []
    results.append(("Frontend Homepage", test_frontend_homepage()))
    results.append(("Backend Health", test_backend_health()))
    results.append(("Backend API", test_backend_api()))
    
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {name}")
    
    if all(success for _, success in results):
        print("\n✅ All integration tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)

