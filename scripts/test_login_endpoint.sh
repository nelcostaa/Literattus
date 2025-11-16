#!/bin/bash
# Test login endpoint directly to see actual error

echo "Testing login endpoint..."
echo "========================="
echo ""

# Test 1: Check if endpoint is accessible
echo "Test 1: GET /login/ (should return 200)"
curl -s -o /dev/null -w "Status: %{http_code}\n" \
  http://literattus-alb-96115082.sa-east-1.elb.amazonaws.com/login/
echo ""

# Test 2: POST with invalid CSRF (should return 403, not 500)
echo "Test 2: POST /login/ without CSRF (should return 403, not 500)"
response=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
  -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=test@test.com&REDACTED=test123" \
  http://literattus-alb-96115082.sa-east-1.elb.amazonaws.com/login/)
http_code=$(echo "$response" | grep "HTTP_CODE" | cut -d: -f2)
body=$(echo "$response" | sed '/HTTP_CODE/d')

echo "HTTP Status: $http_code"
if [ "$http_code" = "500" ]; then
    echo "❌ ERROR: Got 500 Internal Server Error!"
    echo "Response body:"
    echo "$body" | head -30
else
    echo "✅ Got expected status code: $http_code"
fi
echo ""

# Test 3: Check backend connectivity from frontend perspective
echo "Test 3: Backend API connectivity"
backend_status=$(curl -s -o /dev/null -w "%{http_code}" \
  http://literattus-alb-96115082.sa-east-1.elb.amazonaws.com/api/auth/login \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","REDACTED":"test123"}')
echo "Backend API Status: $backend_status"
echo ""

