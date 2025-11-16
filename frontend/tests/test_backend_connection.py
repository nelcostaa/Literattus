"""
Test backend connection and URL handling.
"""

import pytest
from unittest.mock import patch, Mock
import requests
from django.conf import settings


class TestBackendConnection:
    """Test backend connection utilities."""
    
    def test_get_backend_url_http(self):
        """Test get_backend_url with HTTP URL."""
        from apps.core.utils import get_backend_url
        
        with patch.object(settings, 'FASTAPI_BACKEND_URL', 'http://localhost:8000'):
            url = get_backend_url()
            assert url == 'http://localhost:8000'
            assert url.startswith('http://')
            assert not url.startswith('https://')
    
    def test_get_backend_url_https_conversion(self):
        """Test get_backend_url converts HTTPS to HTTP."""
        from apps.core.utils import get_backend_url
        
        with patch.object(settings, 'FASTAPI_BACKEND_URL', 'https://example.com'):
            url = get_backend_url()
            assert url == 'http://example.com'
            assert not url.startswith('https://')
    
    def test_get_backend_url_alb_url(self):
        """Test get_backend_url with ALB URL."""
        from apps.core.utils import get_backend_url
        
        alb_url = 'http://literattus-alb-96115082.sa-east-1.elb.amazonaws.com'
        with patch.object(settings, 'FASTAPI_BACKEND_URL', alb_url):
            url = get_backend_url()
            assert url == alb_url
            assert url.startswith('http://')
    
    @patch('apps.core.views.requests.post')
    def test_login_request_url_format(self, mock_post):
        """Test that login request uses correct URL format."""
        from apps.core.views import login_view
        from django.test import RequestFactory
        
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {'detail': 'Invalid credentials'}
        mock_post.return_value = mock_response
        
        # Create request
        factory = RequestFactory()
        request = factory.post('/login/', {
            'email': 'test@example.com',
            'REDACTED': 'test123'
        })
        
        # Add session
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        
        # Call view
        with patch.object(settings, 'FASTAPI_BACKEND_URL', 'http://backend.example.com'):
            from apps.core.views import get_backend_url
            login_view(request)
        
        # Verify request was made with HTTP
        assert mock_post.called
        call_url = mock_post.call_args[0][0]
        assert call_url.startswith('http://')
        assert not call_url.startswith('https://')
        assert '/api/auth/login' in call_url

