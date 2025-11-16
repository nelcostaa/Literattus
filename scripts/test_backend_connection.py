#!/usr/bin/env python3
"""
Test script to verify backend API connectivity.
Tests both local and AWS endpoints.
"""

import requests
import sys
import json
from typing import Dict, Tuple

def test_endpoint(url: str, method: str = "GET", data: dict = None, headers: dict = None) -> Tuple[bool, Dict]:
    """Test an API endpoint and return success status and response."""
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        else:
            return False, {"error": f"Unsupported method: {method}"}
        
        return response.status_code < 500, {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response.text[:500] if response.text else None
        }
    except requests.exceptions.RequestException as e:
        return False, {"error": str(e)}

def main():
    """Run connectivity tests."""
    print("=" * 70)
    print("Backend API Connectivity Test")
    print("=" * 70)
    
    # Test endpoints
    endpoints = [
        ("http://localhost:8000/health", "GET", None, "Local health check"),
        ("http://localhost:8000/api/health", "GET", None, "Local API health (should 404)"),
        ("http://literattus-alb-96115082.sa-east-1.elb.amazonaws.com/health", "GET", None, "AWS health check"),
        ("http://literattus-alb-96115082.sa-east-1.elb.amazonaws.com/api/health", "GET", None, "AWS API health (should 404)"),
        ("http://literattus-alb-96115082.sa-east-1.elb.amazonaws.com/api/auth/login", "POST", 
         {"email": "test@test.com", "REDACTED": "test123"}, "AWS login endpoint"),
    ]
    
    results = []
    for url, method, data, description in endpoints:
        print(f"\n🔍 Testing: {description}")
        print(f"   URL: {url}")
        success, result = test_endpoint(url, method, data)
        
        if success:
            print(f"   ✅ Status: {result.get('status_code', 'N/A')}")
            if result.get('body'):
                try:
                    body_json = json.loads(result['body'])
                    print(f"   Response: {json.dumps(body_json, indent=2)[:200]}")
                except:
                    print(f"   Response: {result['body'][:200]}")
        else:
            print(f"   ❌ Failed: {result.get('error', result.get('status_code', 'Unknown'))}")
            if result.get('body'):
                print(f"   Response: {result['body'][:200]}")
        
        results.append((description, success, result))
    
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    
    for desc, success, _ in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {desc}")
    
    # Exit with error if any test failed
    if not all(success for _, success, _ in results):
        sys.exit(1)

if __name__ == "__main__":
    main()

