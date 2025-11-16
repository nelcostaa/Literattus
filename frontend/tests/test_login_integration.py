"""
Integration tests for login functionality.
Tests the full login flow including backend communication.
"""

import pytest
from unittest.mock import patch, Mock
from django.test import Client
from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.storage.fallback import FallbackStorage


class TestLoginIntegration:
    """Test login integration with backend API."""
    
    @pytest.fixture
    def client(self):
        """Django test client."""
        return Client()
    
    @pytest.fixture
    def mock_backend_response(self):
        """Mock successful backend login response."""
        return {
            'access_token': 'test_access_token',
            'refresh_token': 'test_refresh_token',
            'token_type': 'bearer',
            'expires_in': 1800
        }
    
    @pytest.fixture
    def mock_user_response(self):
        """Mock user data response."""
        return {
            'id': 1,
            'email': 'test@example.com',
            'firstName': 'Test',
            'lastName': 'User',
            'username': 'testuser'
        }
    
    def test_login_success(self, client, mock_backend_response, mock_user_response):
        """Test successful login flow."""
        with patch('apps.core.views.requests.post') as mock_post, \
             patch('apps.core.views.requests.get') as mock_get:
            
            # Mock login response
            mock_login_response = Mock()
            mock_login_response.status_code = 200
            mock_login_response.json.return_value = mock_backend_response
            mock_post.return_value = mock_login_response
            
            # Mock user data response
            mock_user_data_response = Mock()
            mock_user_data_response.status_code = 200
            mock_user_data_response.json.return_value = mock_user_response
            mock_get.return_value = mock_user_data_response
            
            # Make login request
            response = client.post(
                reverse('core:login'),
                {
                    'email': 'test@example.com',
                    'REDACTED': 'testREDACTED123'
                }
            )
            
            # Verify redirect to dashboard
            assert response.status_code == 302
            assert response.url == '/dashboard/'
            
            # Verify session data
            assert 'access_token' in client.session
            assert client.session['access_token'] == 'test_access_token'
            assert client.session['user_id'] == 1
            assert client.session['user_email'] == 'test@example.com'
            
            # Verify API calls
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert 'http://' in call_args[0][0]  # Should use HTTP, not HTTPS
            assert '/api/auth/login' in call_args[0][0]
            
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert 'http://' in call_args[0][0]  # Should use HTTP, not HTTPS
            assert '/api/auth/me' in call_args[0][0]
            assert 'Authorization' in call_args[1]['headers']
            assert 'Bearer test_access_token' in call_args[1]['headers']['Authorization']
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        with patch('apps.core.views.requests.post') as mock_post:
            # Mock failed login response
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.json.return_value = {'detail': 'Incorrect email or REDACTED'}
            mock_post.return_value = mock_response
            
            # Make login request
            response = client.post(
                reverse('core:login'),
                {
                    'email': 'test@example.com',
                    'REDACTED': 'wrongREDACTED'
                }
            )
            
            # Should render login page with error
            assert response.status_code == 200
            assert 'Invalid email or REDACTED' in str(response.content)
            
            # Session should not have access_token
            assert 'access_token' not in client.session
    
    def test_login_backend_connection_error(self, client):
        """Test login when backend is unreachable."""
        with patch('apps.core.views.requests.post') as mock_post:
            # Mock connection error
            import requests
            mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")
            
            # Make login request
            response = client.post(
                reverse('core:login'),
                {
                    'email': 'test@example.com',
                    'REDACTED': 'testREDACTED123'
                }
            )
            
            # Should render login page with error
            assert response.status_code == 200
            assert 'Unable to connect' in str(response.content) or 'authentication service' in str(response.content)
    
    def test_login_backend_500_error(self, client):
        """Test login when backend returns 500."""
        with patch('apps.core.views.requests.post') as mock_post:
            # Mock 500 response
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = 'Internal Server Error'
            mock_post.return_value = mock_response
            
            # Make login request
            response = client.post(
                reverse('core:login'),
                {
                    'email': 'test@example.com',
                    'REDACTED': 'testREDACTED123'
                }
            )
            
            # Should handle gracefully
            assert response.status_code in [200, 500]  # May return 500 or render error page
            # Should not crash with unhandled exception
    
    def test_backend_url_uses_http(self):
        """Test that get_backend_url() always returns HTTP URL."""
        from apps.core.utils import get_backend_url
        from django.conf import settings
        
        # Test with HTTP URL
        with patch.object(settings, 'FASTAPI_BACKEND_URL', 'http://example.com'):
            assert get_backend_url() == 'http://example.com'
        
        # Test with HTTPS URL (should be converted to HTTP)
        with patch.object(settings, 'FASTAPI_BACKEND_URL', 'https://example.com'):
            assert get_backend_url() == 'http://example.com'
        
        # Test with ALB URL
        with patch.object(settings, 'FASTAPI_BACKEND_URL', 'http://literattus-alb-96115082.sa-east-1.elb.amazonaws.com'):
            result = get_backend_url()
            assert result.startswith('http://')
            assert not result.startswith('https://')
    
    def test_login_requests_use_http(self, client, mock_backend_response, mock_user_response):
        """Test that login requests use HTTP protocol."""
        with patch('apps.core.views.requests.post') as mock_post, \
             patch('apps.core.views.requests.get') as mock_get:
            
            # Mock responses
            mock_login_response = Mock()
            mock_login_response.status_code = 200
            mock_login_response.json.return_value = mock_backend_response
            mock_post.return_value = mock_login_response
            
            mock_user_data_response = Mock()
            mock_user_data_response.status_code = 200
            mock_user_data_response.json.return_value = mock_user_response
            mock_get.return_value = mock_user_data_response
            
            # Make login request
            client.post(
                reverse('core:login'),
                {
                    'email': 'test@example.com',
                    'REDACTED': 'testREDACTED123'
                }
            )
            
            # Verify all requests use HTTP
            for call in mock_post.call_args_list:
                url = call[0][0]
                assert url.startswith('http://'), f"URL should use HTTP: {url}"
                assert not url.startswith('https://'), f"URL should not use HTTPS: {url}"
            
            for call in mock_get.call_args_list:
                url = call[0][0]
                assert url.startswith('http://'), f"URL should use HTTP: {url}"
                assert not url.startswith('https://'), f"URL should not use HTTPS: {url}"

