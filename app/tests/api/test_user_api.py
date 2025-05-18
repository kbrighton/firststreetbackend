import pytest
import json
from flask import url_for

class TestUserAPI:
    """Integration tests for User API endpoints."""

    @pytest.fixture
    def admin_user_data(self):
        """Admin user data for tests."""
        return {
            'username': 'adminuser',
            'email': 'admin@example.com',
            'password': 'adminpass123',
            'role': 'admin'
        }

    @pytest.fixture
    def admin_user(self, db_session, admin_user_data):
        """Create an admin user for tests."""
        from app.models.user import User
        user = User(
            username=admin_user_data['username'],
            email=admin_user_data['email'],
            role=admin_user_data['role']
        )
        user.set_password(admin_user_data['password'])
        db_session.add(user)
        db_session.commit()
        return user

    def test_get_users_as_admin(self, client, admin_user, admin_user_data, sample_user):
        """Test getting all users as admin."""
        # Login as admin
        client.post(
            '/api/auth/login',
            json={
                'username': admin_user_data['username'],
                'password': admin_user_data['password']
            }
        )

        response = client.get('/api/users')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 2  # At least admin_user and sample_user
        
        # Check if both users are in the response
        usernames = [user['username'] for user in data]
        assert admin_user_data['username'] in usernames
        assert 'testuser' in usernames  # sample_user username

    def test_get_users_as_regular_user(self, client, sample_user, valid_user_data):
        """Test getting all users as a regular user (should be forbidden)."""
        # Login as regular user
        client.post(
            '/api/auth/login',
            json={
                'username': valid_user_data['username'],
                'password': valid_user_data['password']
            }
        )

        response = client.get('/api/users')
        assert response.status_code == 403  # Forbidden

    def test_get_user_by_id_as_admin(self, client, admin_user, admin_user_data, sample_user):
        """Test getting a specific user by ID as admin."""
        # Login as admin
        client.post(
            '/api/auth/login',
            json={
                'username': admin_user_data['username'],
                'password': admin_user_data['password']
            }
        )

        response = client.get(f'/api/users/{sample_user.id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == sample_user.id
        assert data['username'] == sample_user.username
        assert data['email'] == sample_user.email
        assert data['role'] == sample_user.role

    def test_create_user_as_admin(self, client, admin_user, admin_user_data):
        """Test creating a new user as admin."""
        # Login as admin
        client.post(
            '/api/auth/login',
            json={
                'username': admin_user_data['username'],
                'password': admin_user_data['password']
            }
        )

        new_user_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'role': 'user'
        }

        response = client.post(
            '/api/users',
            json=new_user_data
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['username'] == new_user_data['username']
        assert data['email'] == new_user_data['email']
        assert data['role'] == new_user_data['role']
        # Password should not be returned

    def test_update_user_as_admin(self, client, admin_user, admin_user_data, sample_user):
        """Test updating a user as admin."""
        # Login as admin
        client.post(
            '/api/auth/login',
            json={
                'username': admin_user_data['username'],
                'password': admin_user_data['password']
            }
        )

        update_data = {
            'username': 'updateduser',
            'email': 'updated@example.com',
            'role': 'admin'  # Change role (only admins can do this)
        }

        response = client.put(
            f'/api/users/{sample_user.id}',
            json=update_data
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == sample_user.id
        assert data['username'] == update_data['username']
        assert data['email'] == update_data['email']
        assert data['role'] == update_data['role']

    def test_update_self_as_regular_user(self, client, sample_user, valid_user_data):
        """Test updating own user info as a regular user."""
        # Login as regular user
        client.post(
            '/api/auth/login',
            json={
                'username': valid_user_data['username'],
                'password': valid_user_data['password']
            }
        )

        update_data = {
            'username': 'updatedregular',
            'email': 'updatedregular@example.com'
            # No role change - regular users can't change roles
        }

        response = client.put(
            f'/api/users/{sample_user.id}',
            json=update_data
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == sample_user.id
        assert data['username'] == update_data['username']
        assert data['email'] == update_data['email']
        assert data['role'] == 'user'  # Role should not change

    def test_update_other_user_as_regular_user(self, client, sample_user, valid_user_data, admin_user):
        """Test updating another user as a regular user (should be forbidden)."""
        # Login as regular user
        client.post(
            '/api/auth/login',
            json={
                'username': valid_user_data['username'],
                'password': valid_user_data['password']
            }
        )

        update_data = {
            'username': 'hacked',
            'email': 'hacked@example.com'
        }

        response = client.put(
            f'/api/users/{admin_user.id}',  # Try to update admin user
            json=update_data
        )
        assert response.status_code == 403  # Forbidden

    def test_delete_user_as_admin(self, client, admin_user, admin_user_data, sample_user):
        """Test deleting a user as admin."""
        # Login as admin
        client.post(
            '/api/auth/login',
            json={
                'username': admin_user_data['username'],
                'password': admin_user_data['password']
            }
        )

        response = client.delete(f'/api/users/{sample_user.id}')
        assert response.status_code == 204

        # Verify the user is deleted
        response = client.get(f'/api/users/{sample_user.id}')
        assert response.status_code == 404

    def test_delete_self_as_admin(self, client, admin_user, admin_user_data):
        """Test deleting self as admin (should be forbidden)."""
        # Login as admin
        client.post(
            '/api/auth/login',
            json={
                'username': admin_user_data['username'],
                'password': admin_user_data['password']
            }
        )

        response = client.delete(f'/api/users/{admin_user.id}')
        assert response.status_code == 403  # Forbidden