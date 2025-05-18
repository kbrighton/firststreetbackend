"""
End-to-end tests for authentication flows.

This module contains tests that verify the login and logout functionality
through the web UI.
"""

import pytest
from flask import url_for
from app.tests.e2e.helpers import login, logout, check_content, check_flash_message


class TestAuthFlows:
    """End-to-end tests for authentication flows."""

    def test_login_success(self, client, sample_user, valid_user_data):
        """Test successful login."""
        # Attempt to access a protected page before login
        response = client.get('/', follow_redirects=True)
        assert response.status_code == 200
        assert 'Sign In' in response.data.decode('utf-8')
        
        # Login with valid credentials
        response = login(
            client, 
            valid_user_data['username'], 
            valid_user_data['password']
        )
        
        # Verify we're logged in and redirected to the home page
        assert response.status_code == 200
        assert 'Sign In' not in response.data.decode('utf-8')
        assert 'Logout' in response.data.decode('utf-8')
    
    def test_login_invalid_credentials(self, client, sample_user):
        """Test login with invalid credentials."""
        # Login with invalid username
        response = login(client, 'nonexistent', 'password123')
        assert check_flash_message(response, 'Invalid username or password')
        
        # Login with invalid password
        response = login(client, 'testuser', 'wrongpassword')
        assert check_flash_message(response, 'Invalid username or password')
    
    def test_logout(self, client, sample_user, valid_user_data):
        """Test logout functionality."""
        # First login
        login(client, valid_user_data['username'], valid_user_data['password'])
        
        # Then logout
        response = logout(client)
        
        # Verify we're logged out and redirected to the login page
        assert response.status_code == 200
        assert 'Sign In' in response.data.decode('utf-8')
        assert 'Logout' not in response.data.decode('utf-8')
        
        # Verify we can't access protected pages
        response = client.get('/', follow_redirects=True)
        assert 'Sign In' in response.data.decode('utf-8')
    
    def test_remember_me(self, client, sample_user, valid_user_data):
        """Test the remember me functionality."""
        # Login with remember me checked
        response = login(
            client, 
            valid_user_data['username'], 
            valid_user_data['password'],
            remember=True
        )
        
        # Check that the session cookie has the remember flag
        cookies = client.cookie_jar
        for cookie in cookies:
            if cookie.name == 'session':
                # The remember flag is set in the cookie's expiration
                assert cookie.expires is not None
                break