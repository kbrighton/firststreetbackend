
import pytest
from flask import url_for
from app.models import User
from sqlalchemy import select

def test_user_list_as_admin(client, app, db_session):
    """Test that an admin can view the user list."""
    with app.test_request_context():
        admin = User(username='admin', email='admin@example.com', role='admin')
        admin.set_password('password')
        db_session.add(admin)
        db_session.commit()

        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin.id)
            sess['_fresh'] = True

        response = client.get(url_for('main.user_list'))
        assert response.status_code == 200
        assert b'User Management' in response.data
        assert b'admin' in response.data

def test_user_list_as_regular_user(client, app, db_session):
    """Test that a regular user can view their own profile but not others."""
    with app.test_request_context():
        user = User(username='user', email='user@example.com', role='user')
        user.set_password('password')
        
        other_user = User(username='other', email='other@example.com', role='user')
        other_user.set_password('password')
        
        db_session.add(user)
        db_session.add(other_user)
        db_session.commit()

        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True

        response = client.get(url_for('main.user_list'))
        assert response.status_code == 200
        assert b'Manage My Profile' in response.data
        assert b'user@example.com' in response.data
        assert b'other@example.com' not in response.data

def test_user_edit_own_profile(client, app, db_session):
    """Test that a regular user can edit their own profile."""
    with app.test_request_context():
        user = User(username='user', email='user@example.com', role='user')
        user.set_password('password')
        db_session.add(user)
        db_session.commit()

        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True

        response = client.post(url_for('main.user_edit', user_id=user.id), data={
            'username': 'updateduser',
            'email': 'updated@example.com',
            'password': 'newpassword123',
            'submit': 'Submit'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'User updateduser updated successfully' in response.data
        
        db_session.refresh(user)
        assert user.username == 'updateduser'
        assert user.check_password('newpassword123')
        assert user.role == 'user'  # Role should not change

def test_user_edit_other_profile_forbidden(client, app, db_session):
    """Test that a regular user cannot edit another user's profile."""
    with app.test_request_context():
        user = User(username='user', email='user@example.com', role='user')
        user.set_password('password')
        
        other_user = User(username='other', email='other@example.com', role='user')
        other_user.set_password('password')
        
        db_session.add(user)
        db_session.add(other_user)
        db_session.commit()

        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True

        response = client.get(url_for('main.user_edit', user_id=other_user.id))
        assert response.status_code == 403

def test_user_create_as_admin(client, app, db_session):
    """Test that an admin can create a new user."""
    with app.test_request_context():
        admin = User(username='admin', email='admin@example.com', role='admin')
        admin.set_password('password')
        db_session.add(admin)
        db_session.commit()

        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin.id)
            sess['_fresh'] = True

        response = client.post(url_for('main.user_new'), data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'password123',
            'role': 'user',
            'submit': 'Submit'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'User newuser created successfully' in response.data
        
        new_user = db_session.execute(select(User).filter_by(username='newuser')).scalar_one_or_none()
        assert new_user is not None
        assert new_user.email == 'new@example.com'

def test_user_edit_as_admin(client, app, db_session):
    """Test that an admin can edit an existing user."""
    with app.test_request_context():
        admin = User(username='admin', email='admin@example.com', role='admin')
        admin.set_password('password')
        
        user = User(username='tobedirected', email='edit@example.com', role='user')
        user.set_password('password')
        
        db_session.add(admin)
        db_session.add(user)
        db_session.commit()

        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin.id)
            sess['_fresh'] = True

        response = client.post(url_for('main.user_edit', user_id=user.id), data={
            'username': 'updateduser',
            'email': 'updated@example.com',
            'role': 'admin',
            'submit': 'Submit'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'User updateduser updated successfully' in response.data
        
        db_session.refresh(user)
        assert user.username == 'updateduser'
        assert user.role == 'admin'

def test_user_delete_as_admin(client, app, db_session):
    """Test that an admin can delete a user."""
    with app.test_request_context():
        admin = User(username='admin', email='admin@example.com', role='admin')
        admin.set_password('password')
        
        user = User(username='tobedeleted', email='delete@example.com', role='user')
        user.set_password('password')
        
        db_session.add(admin)
        db_session.add(user)
        db_session.commit()

        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin.id)
            sess['_fresh'] = True

        response = client.post(url_for('main.user_delete', user_id=user.id), follow_redirects=True)
        
        assert response.status_code == 200
        assert b'User tobedeleted deleted successfully' in response.data
        
        deleted_user = db_session.get(User, user.id)
        assert deleted_user.deleted_at is not None
