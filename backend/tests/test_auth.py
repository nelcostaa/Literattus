"""
Tests for authentication endpoints.
"""

import pytest


def test_register_user(client):
    """Test user registration."""
    response = client.post("/api/auth/register", json={
        "email": "newuser@example.com",
        "password": "securepassword123",
        "firstName": "New",
        "lastName": "User"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["firstName"] == "New"
    assert data["lastName"] == "User"
    assert "password" not in data


def test_register_duplicate_email(client, test_user):
    """Test registration with existing email."""
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",  # Already exists
        "password": "password123",
        "firstName": "Duplicate",
        "lastName": "User"
    })
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_login_success(client, test_user):
    """Test successful login."""
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "testpassword123"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client, test_user):
    """Test login with invalid credentials."""
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401


def test_get_current_user(client, auth_headers):
    """Test getting current user info."""
    response = client.get("/api/auth/me", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "password" not in data


def test_get_current_user_unauthorized(client):
    """Test getting current user without authentication."""
    response = client.get("/api/auth/me")
    
    assert response.status_code == 403  # No auth header

