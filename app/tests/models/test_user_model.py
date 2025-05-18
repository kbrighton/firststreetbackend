import pytest
from app.models.user import User
from app.extensions import db
from sqlalchemy.exc import IntegrityError


class TestUserModel:
    """Test suite for the User model."""

    def test_create_valid_user(self, db_session, valid_user_data):
        """Test creating a valid user."""
        user = User(
            username=valid_user_data['username'],
            email=valid_user_data['email'],
            role=valid_user_data['role']
        )
        user.set_password(valid_user_data['password'])
        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.username == valid_user_data['username']
        assert user.email == valid_user_data['email']
        assert user.role == valid_user_data['role']
        assert user.password_hash is not None
        assert user.password_hash != valid_user_data['password']  # Password should be hashed
        assert user.created_at is not None
        assert user.updated_at is not None
        assert user.deleted_at is None

    def test_user_representation(self, sample_user):
        """Test the string representation of a user."""
        assert str(sample_user) == f'<User {sample_user.username}>'
        assert repr(sample_user) == f'<User {sample_user.username}>'

    def test_validate_data_valid_user(self, sample_user):
        """Test validate_data with a valid user."""
        errors = sample_user.validate_data()
        assert errors == {}

    def test_validate_data_invalid_user(self, db_session, invalid_user_data):
        """Test validate_data with an invalid user."""
        user = User(
            username=invalid_user_data['username'],
            email=invalid_user_data['email'],
            role=invalid_user_data['role']
        )
        errors = user.validate_data()
        
        assert 'username' in errors
        assert 'email' in errors
        assert 'role' in errors

    def test_validate_user_event_listener(self, db_session, invalid_user_data):
        """Test that the validate_user event listener prevents invalid users from being saved."""
        user = User(
            username=invalid_user_data['username'],
            email=invalid_user_data['email'],
            role=invalid_user_data['role']
        )
        db_session.add(user)
        
        with pytest.raises(ValueError) as excinfo:
            db_session.commit()
        
        assert "User validation failed" in str(excinfo.value)
        db_session.rollback()

    def test_unique_username_constraint(self, db_session, valid_user_data, sample_user):
        """Test that username must be unique."""
        # Try to create second user with same username
        user2 = User(
            username=sample_user.username,
            email="different@example.com",
            role="user"
        )
        db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        db_session.rollback()

    def test_unique_email_constraint(self, db_session, valid_user_data, sample_user):
        """Test that email must be unique."""
        # Try to create second user with same email
        user2 = User(
            username="different",
            email=sample_user.email,
            role="user"
        )
        db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        db_session.rollback()

    def test_set_password(self, db_session):
        """Test setting a password."""
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        
        assert user.password_hash is not None
        assert user.password_hash != "password123"  # Password should be hashed

    def test_check_password(self, sample_user, valid_user_data):
        """Test checking a password."""
        assert sample_user.check_password(valid_user_data['password']) is True
        assert sample_user.check_password("wrongpassword") is False

    def test_validate_length(self):
        """Test the _validate_length method."""
        assert User._validate_length("username", 3, 64) is True
        assert User._validate_length("us", 3, 64) is False
        assert User._validate_length("a" * 65, 3, 64) is False
        assert User._validate_length("", 0) is True
        assert User._validate_length("", 1) is False
        assert User._validate_length(None, 0) is True
        assert User._validate_length(None, 1) is False

    def test_validate_email(self):
        """Test the _validate_email method."""
        assert User._validate_email("test@example.com") is True
        assert User._validate_email("invalid-email") is False
        assert User._validate_email("") is False
        assert User._validate_email(None) is False

    def test_soft_delete(self, db_session, sample_user):
        """Test soft deleting a user."""
        # Set deleted_at timestamp
        sample_user.deleted_at = db.func.current_timestamp()
        db_session.commit()
        
        # Verify user is soft deleted
        assert sample_user.deleted_at is not None
        
        # Verify user is not returned in normal queries
        from app.repositories.user_repository import UserRepository
        repo = UserRepository()
        users = repo.get_all()
        assert sample_user not in users
        
        # Verify user is returned in queries that include deleted
        deleted_users = repo.get_deleted()
        assert sample_user in deleted_users