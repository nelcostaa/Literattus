#!/bin/bash
# Test login with proper CSRF token handling

echo "Testing login with CSRF token..."
echo "=================================="
echo ""

# Step 1: Get CSRF token from login page
echo "Step 1: Getting CSRF token..."
csrf_response=$(curl -s -c /tmp/cookies.txt http://literattus-alb-96115082.sa-east-1.elb.amazonaws.com/login/)
csrf_token=$(echo "$csrf_response" | grep -oP 'name="csrfmiddlewaretoken" value="\K[^"]+' || echo "")

if [ -z "$csrf_token" ]; then
    echo "❌ Could not extract CSRF token"
    echo "Response preview:"
    echo "$csrf_response" | head -20
    exit 1
fi

echo "✅ CSRF token obtained: ${csrf_token:0:20}..."
echo ""

# Step 2: Attempt login with CSRF token
echo "Step 2: Attempting login with CSRF token..."
login_response=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
    -b /tmp/cookies.txt \
    -c /tmp/cookies.txt \
    -X POST \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -H "Referer: http://literattus-alb-96115082.sa-east-1.elb.amazonaws.com/login/" \
    -d "csrfmiddlewaretoken=$csrf_token&email=test@test.com&REDACTED=test123" \
    http://literattus-alb-96115082.sa-east-1.elb.amazonaws.com/login/)

http_code=$(echo "$login_response" | grep "HTTP_CODE" | cut -d: -f2)
body=$(echo "$login_response" | sed '/HTTP_CODE/d')

echo "HTTP Status: $http_code"
echo ""

if [ "$http_code" = "500" ]; then
    echo "❌ ERROR: Got 500 Internal Server Error!"
    echo ""
    echo "Response body (first 500 chars):"
    echo "$body" | head -c 500
    echo ""
    echo ""
    echo "Checking for error messages..."
    echo "$body" | grep -i "error\|exception\|traceback" | head -10
    exit 1
elif [ "$http_code" = "302" ]; then
    location=$(echo "$login_response" | grep -i "location:" | cut -d: -f2- | tr -d '\r\n ')
    echo "✅ Got redirect (302) - Login may have succeeded"
    echo "Redirect location: $location"
elif [ "$http_code" = "200" ]; then
    echo "✅ Got 200 OK - Checking for error messages..."
    if echo "$body" | grep -qi "invalid\|error\|failed"; then
        echo "⚠️  Page contains error messages (may be expected for invalid credentials)"
        echo "$body" | grep -i "invalid\|error\|failed" | head -5
    else
        echo "✅ Page loaded successfully"
    fi
else
    echo "⚠️  Got unexpected status code: $http_code"
fi

# Cleanup
rm -f /tmp/cookies.txt

