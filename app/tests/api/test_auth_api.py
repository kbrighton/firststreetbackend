import pytest
import json
from flask import url_for

class TestAuthAPI:
    """Integration tests for Authentication API endpoints."""

    def test_login(self, client, sample_user, valid_user_data):
        """Test login endpoint."""
        # Test with valid credentials
        response = client.post(
            '/api/auth/login',
            json={
                'username': valid_user_data['username'],
                'password': valid_user_data['password']
            }
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
        assert data['message'] == 'Login successful'
        assert 'user' in data
        assert data['user']['username'] == valid_user_data['username']

        # Test with invalid username
        response = client.post(
            '/api/auth/login',
            json={
                'username': 'nonexistent',
                'password': valid_user_data['password']
            }
        )
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'message' in data
        assert 'Invalid username or password' in data['message']

        # Test with invalid password
        response = client.post(
            '/api/auth/login',
            json={
                'username': valid_user_data['username'],
                'password': 'wrongpassword'
            }
        )
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'message' in data
        assert 'Invalid username or password' in data['message']

        # Test with missing credentials
        response = client.post(
            '/api/auth/login',
            json={}
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'message' in data
        assert 'Username and password required' in data['message']

    def test_logout(self, client, sample_user, valid_user_data):
        """Test logout endpoint."""
        # First login
        client.post(
            '/api/auth/login',
            json={
                'username': valid_user_data['username'],
                'password': valid_user_data['password']
            }
        )

        # Then logout
        response = client.post('/api/auth/logout')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
        assert data['message'] == 'Logout successful'

        # Verify we're logged out by trying to access a protected endpoint
        response = client.get('/api/orders')
        assert response.status_code == 401

    def test_me_requires_login(self, client):
        """The current-user endpoint returns 401 JSON when logged out."""
        response = client.get('/api/auth/me')
        assert response.status_code == 401
        assert response.is_json
        assert response.get_json() == {
            'error': 'Unauthorized',
            'message': 'Authentication is required to access this resource',
            'status': 401,
        }

    def test_me_returns_current_user_with_role(self, client, sample_user, valid_user_data):
        """The current-user endpoint returns id, username, email and role."""
        client.post(
            '/api/auth/login',
            json={
                'username': valid_user_data['username'],
                'password': valid_user_data['password']
            }
        )

        response = client.get('/api/auth/me')
        assert response.status_code == 200
        assert response.get_json() == {
            'user': {
                'id': sample_user.id,
                'username': sample_user.username,
                'email': sample_user.email,
                'role': 'user',
                'created_at': sample_user.created_at.isoformat(),
            }
        }

    def test_csrf_endpoint_returns_token(self, client):
        """The CSRF endpoint returns a token without requiring login."""
        response = client.get('/api/auth/csrf')
        assert response.status_code == 200
        token = response.get_json()['csrf_token']
        assert isinstance(token, str) and token