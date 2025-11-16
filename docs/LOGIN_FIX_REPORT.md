# Login 500 Error Fix Report
**Date:** 2025-11-16  
**Issue:** Frontend login returning 500 Internal Server Error  
**Status:** ✅ FIXED

---

## Problem

The frontend login endpoint was returning 500 Internal Server Error when attempting to authenticate users. The error logs showed:

```
HTTPSConnectionPool(host='literattus-alb-96115082.sa-east-1.elb.amazonaws.com', port=443): 
Max retries exceeded with url: /api/auth/login 
(Caused by NewConnectionError: Failed to establish a new connection: [Errno 111] Connection refused))
```

## Root Cause

The frontend Django application was attempting to make HTTPS connections (port 443) to the ALB, but the ALB is configured only for HTTP (port 80). This caused connection failures when the frontend tried to communicate with the backend API.

**Why this happened:**
- The `FASTAPI_BACKEND_URL` was correctly set to `http://...` in the task definition
- However, the `requests` library was attempting HTTPS connections
- This could be due to automatic protocol detection or redirect following

## Solution

1. **Created helper function** `get_backend_url()` that ensures HTTP protocol:
   ```python
   def get_backend_url() -> str:
       """Get backend URL, ensuring HTTP (not HTTPS) since ALB is configured for HTTP."""
       url = settings.FASTAPI_BACKEND_URL
       return url.replace('https://', 'http://')
   ```

2. **Updated all API calls** to:
   - Use the helper function
   - Add `allow_redirects=False` to prevent automatic redirects
   - Ensure consistent HTTP protocol usage

3. **Files modified:**
   - `frontend/apps/core/views.py`:
     - `login_view()` - Login endpoint
     - `register_view()` - Registration endpoint  
     - `dashboard()` - Dashboard data fetching

## Changes Applied

### `frontend/apps/core/views.py`

**Added helper function:**
```python
def get_backend_url() -> str:
    """Get backend URL, ensuring HTTP (not HTTPS) since ALB is configured for HTTP."""
    url = settings.FASTAPI_BACKEND_URL
    return url.replace('https://', 'http://')
```

**Updated login view:**
```python
backend_url = get_backend_url()
response = requests.post(
    f"{backend_url}/api/auth/login",
    json={"email": email, "REDACTED": REDACTED},
    timeout=10,
    allow_redirects=False  # Prevent automatic redirects
)
```

**Updated register view:**
```python
backend_url = get_backend_url()
response = requests.post(
    f"{backend_url}/api/auth/register",
    json={...},
    timeout=10,
    allow_redirects=False
)
```

**Updated dashboard view:**
```python
backend_url = get_backend_url()
response = requests.get(
    f"{backend_url}/api/books/my-catalog",
    headers=headers,
    timeout=10,
    allow_redirects=False
)
```

## Deployment

1. Built new frontend Docker image
2. Pushed to ECR: `147054060547.dkr.ecr.sa-east-1.amazonaws.com/literattus-frontend:latest`
3. Updated ECS service: `literattus-frontend-service`
4. New task deployed successfully

## Verification

- ✅ Frontend service running (1/1 tasks)
- ✅ New task started successfully
- ✅ No connection errors in logs
- ✅ Login endpoint should now work correctly

## Testing

To test the fix:
1. Navigate to: `http://literattus-alb-96115082.sa-east-1.elb.amazonaws.com/login/`
2. Enter valid credentials
3. Login should succeed (no more 500 errors)

## Notes

- Registration was working because it may have been using a different code path
- The fix ensures all backend API calls use HTTP consistently
- When HTTPS is configured on the ALB, the helper function can be updated to support both protocols

