import pytest
from unittest.mock import MagicMock, patch
from app.services.user_service import UserService
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.utils.validation import validate_and_sanitize_user_data, sanitize_string


class TestUserService:
    """Test suite for the UserService class."""

    @pytest.fixture
    def mock_repository(self):
        """Create a mock repository for testing."""
        repo = MagicMock(spec=UserRepository)
        repo.get_by_id.return_value = MagicMock(spec=User, id=1, username="testuser", email="test@example.com", role="user")
        repo.get_by_username.return_value = MagicMock(spec=User, id=1, username="testuser", email="test@example.com", role="user")
        repo.get_by_email.return_value = MagicMock(spec=User, id=1, username="testuser", email="test@example.com", role="user")
        repo.create.return_value = MagicMock(spec=User, id=1, username="testuser", email="test@example.com", role="user", set_password=MagicMock())
        repo.update.return_value = MagicMock(spec=User, id=1, username="testuser", email="test@example.com", role="user")
        repo.get_all.return_value = [MagicMock(spec=User, id=i, username=f"user{i}", email=f"user{i}@example.com", role="user") for i in range(1, 4)]
        repo.authenticate.return_value = MagicMock(spec=User, id=1, username="testuser", email="test@example.com", role="user")
        return repo

    @pytest.fixture
    def service(self, mock_repository):
        """Create a UserService instance for testing."""
        with patch('app.services.user_service.UserRepository', return_value=mock_repository):
            return UserService(user_repository=mock_repository)

    def test_init_with_repository(self, mock_repository):
        """Test initializing with a repository."""
        service = UserService(user_repository=mock_repository)
        assert service.repository is mock_repository

    def test_init_without_repository(self):
        """Test initializing without a repository."""
        with patch('app.services.user_service.UserRepository') as mock_repo_class:
            mock_repo_instance = MagicMock()
            mock_repo_class.return_value = mock_repo_instance
            
            service = UserService()
            
            mock_repo_class.assert_called_once()
            assert service.repository is mock_repo_instance

    def test_get_user_by_id(self, service, mock_repository):
        """Test getting a user by ID."""
        user = service.get_user_by_id(1)
        
        mock_repository.get_by_id.assert_called_once_with(1)
        assert user is not None
        assert user.id == 1
        assert user.username == "testuser"

    def test_get_user_by_username(self, service, mock_repository):
        """Test getting a user by username."""
        user = service.get_user_by_username("testuser")
        
        mock_repository.get_by_username.assert_called_once_with("testuser")
        assert user is not None
        assert user.username == "testuser"

    def test_get_user_by_email(self, service, mock_repository):
        """Test getting a user by email."""
        user = service.get_user_by_email("test@example.com")
        
        mock_repository.get_by_email.assert_called_once_with("test@example.com")
        assert user is not None
        assert user.email == "test@example.com"

    def test_create_user(self, service, mock_repository):
        """Test creating a user."""
        with patch('app.services.user_service.validate_and_sanitize_user_data') as mock_validate, \
             patch('app.services.user_service.sanitize_string') as mock_sanitize:
            
            mock_sanitize.side_effect = lambda x: x  # Just return the input
            mock_validate.return_value = {
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123",
                "role": "user"
            }
            
            # Mock that user doesn't exist yet
            mock_repository.get_by_username.return_value = None
            mock_repository.get_by_email.return_value = None
            
            user = service.create_user(
                username="testuser",
                email="test@example.com",
                password="password123",
                role="user"
            )
            
            # Check sanitize calls
            assert mock_sanitize.call_count == 3  # username, email, role
            
            # Check validate call
            mock_validate.assert_called_once()
            
            # Check repository calls
            mock_repository.get_by_username.assert_called_once_with("testuser")
            mock_repository.get_by_email.assert_called_once_with("test@example.com")
            mock_repository.create.assert_called_once()
            
            # Check user was created
            assert user is not None
            assert user.id == 1
            assert user.username == "testuser"
            assert user.email == "test@example.com"
            assert user.role == "user"
            
            # Check password was set
            user.set_password.assert_called_once_with("password123")

    def test_create_user_existing_username(self, service, mock_repository):
        """Test creating a user with an existing username."""
        with patch('app.services.user_service.validate_and_sanitize_user_data') as mock_validate, \
             patch('app.services.user_service.sanitize_string') as mock_sanitize:
            
            mock_sanitize.side_effect = lambda x: x  # Just return the input
            mock_validate.return_value = {
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123",
                "role": "user"
            }
            
            # Mock that username already exists
            mock_repository.get_by_username.return_value = MagicMock(spec=User, id=1, username="testuser")
            
            with pytest.raises(ValueError) as excinfo:
                service.create_user(
                    username="testuser",
                    email="test@example.com",
                    password="password123",
                    role="user"
                )
            
            assert "User with username testuser already exists" in str(excinfo.value)

    def test_create_user_existing_email(self, service, mock_repository):
        """Test creating a user with an existing email."""
        with patch('app.services.user_service.validate_and_sanitize_user_data') as mock_validate, \
             patch('app.services.user_service.sanitize_string') as mock_sanitize:
            
            mock_sanitize.side_effect = lambda x: x  # Just return the input
            mock_validate.return_value = {
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123",
                "role": "user"
            }
            
            # Mock that username doesn't exist but email does
            mock_repository.get_by_username.return_value = None
            mock_repository.get_by_email.return_value = MagicMock(spec=User, id=1, email="test@example.com")
            
            with pytest.raises(ValueError) as excinfo:
                service.create_user(
                    username="testuser",
                    email="test@example.com",
                    password="password123",
                    role="user"
                )
            
            assert "User with email test@example.com already exists" in str(excinfo.value)

    def test_update_user(self, service, mock_repository):
        """Test updating a user."""
        with patch('app.services.user_service.validate_and_sanitize_user_data') as mock_validate:
            mock_validate.return_value = {
                "username": "updated_user",
                "email": "updated@example.com",
                "role": "admin"
            }
            
            # Mock that new username and email don't exist
            mock_repository.get_by_username.return_value = None
            mock_repository.get_by_email.return_value = None
            
            user = MagicMock(spec=User, id=1, username="testuser", email="test@example.com", role="user")
            user_data = {
                "username": "updated_user",
                "email": "updated@example.com",
                "role": "admin"
            }
            
            updated_user = service.update_user(user, user_data)
            
            mock_validate.assert_called_once_with(user_data)
            mock_repository.update.assert_called_once()
            assert updated_user is not None
            assert updated_user.id == 1

    def test_update_user_with_password(self, service, mock_repository):
        """Test updating a user with a new password."""
        with patch('app.services.user_service.validate_and_sanitize_user_data') as mock_validate:
            mock_validate.return_value = {
                "username": "testuser",
                "email": "test@example.com",
                "password": "newpassword",
                "role": "user"
            }
            
            user = MagicMock(spec=User, id=1, username="testuser", email="test@example.com", role="user")
            user_data = {
                "password": "newpassword"
            }
            
            updated_user = service.update_user(user, user_data)
            
            mock_validate.assert_called_once_with(user_data)
            user.set_password.assert_called_once_with("newpassword")
            mock_repository.update.assert_called()
            assert updated_user is not None
            assert updated_user.id == 1

    def test_update_user_existing_username(self, service, mock_repository):
        """Test updating a user with an existing username."""
        with patch('app.services.user_service.validate_and_sanitize_user_data') as mock_validate:
            mock_validate.return_value = {
                "username": "existing_user"
            }
            
            # Mock that new username already exists for a different user
            existing_user = MagicMock(spec=User, id=2, username="existing_user")
            mock_repository.get_by_username.return_value = existing_user
            
            user = MagicMock(spec=User, id=1, username="testuser", email="test@example.com", role="user")
            user_data = {
                "username": "existing_user"
            }
            
            with pytest.raises(ValueError) as excinfo:
                service.update_user(user, user_data)
            
            assert "User with username existing_user already exists" in str(excinfo.value)

    def test_delete_user(self, service, mock_repository):
        """Test soft deleting a user."""
        user = MagicMock(spec=User, id=1, username="testuser")
        
        service.delete_user(user)
        
        mock_repository.delete.assert_called_once_with(user)

    def test_hard_delete_user(self, service, mock_repository):
        """Test hard deleting a user."""
        user = MagicMock(spec=User, id=1, username="testuser")
        
        service.hard_delete_user(user)
        
        mock_repository.hard_delete.assert_called_once_with(user)

    def test_restore_user(self, service, mock_repository):
        """Test restoring a soft-deleted user."""
        user = MagicMock(spec=User, id=1, username="testuser", deleted_at="2023-01-01")
        mock_repository.restore.return_value = MagicMock(spec=User, id=1, username="testuser", deleted_at=None)
        
        restored_user = service.restore_user(user)
        
        mock_repository.restore.assert_called_once_with(user)
        assert restored_user is not None
        assert restored_user.id == 1
        assert restored_user.username == "testuser"
        assert restored_user.deleted_at is None

    def test_get_deleted_users(self, service, mock_repository):
        """Test getting all soft-deleted users."""
        mock_repository.get_deleted.return_value = [
            MagicMock(spec=User, id=i, username=f"user{i}", deleted_at="2023-01-01") 
            for i in range(4, 6)
        ]
        
        deleted_users = service.get_deleted_users()
        
        mock_repository.get_deleted.assert_called_once()
        assert len(deleted_users) == 2
        assert all(hasattr(user, 'deleted_at') for user in deleted_users)

    def test_get_all_users_including_deleted(self, service, mock_repository):
        """Test getting all users including soft-deleted ones."""
        mock_repository.get_all_including_deleted.return_value = [
            MagicMock(spec=User, id=i, username=f"user{i}") for i in range(1, 6)
        ]
        
        all_users = service.get_all_users_including_deleted()
        
        mock_repository.get_all_including_deleted.assert_called_once()
        assert len(all_users) == 5

    def test_authenticate_user(self, service, mock_repository):
        """Test authenticating a user."""
        with patch('app.services.user_service.sanitize_string') as mock_sanitize:
            mock_sanitize.return_value = "testuser"
            
            user = service.authenticate_user("testuser", "password123")
            
            mock_sanitize.assert_called_once_with("testuser")
            mock_repository.authenticate.assert_called_once_with("testuser", "password123")
            assert user is not None
            assert user.id == 1
            assert user.username == "testuser"

    def test_authenticate_user_failed(self, service, mock_repository):
        """Test failed authentication."""
        with patch('app.services.user_service.sanitize_string') as mock_sanitize:
            mock_sanitize.return_value = "testuser"
            mock_repository.authenticate.return_value = None
            
            user = service.authenticate_user("testuser", "wrongpassword")
            
            mock_sanitize.assert_called_once_with("testuser")
            mock_repository.authenticate.assert_called_once_with("testuser", "wrongpassword")
            assert user is None

    def test_get_all_users(self, service, mock_repository):
        """Test getting all users."""
        users = service.get_all_users()
        
        mock_repository.get_all.assert_called_once()
        assert len(users) == 3