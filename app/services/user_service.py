"""
User service module for managing user-related business logic.

This module provides a service class that encapsulates all business logic related to users,
including authentication, authorization, CRUD operations, and data validation.
It handles user creation, updates, deletion, and authentication while ensuring data integrity
and security.
"""

from typing import List, Optional, Dict, Any, Union
from app.models import User
from app.repositories.user_repository import UserRepository
from app.logging import get_logger
from app.utils.validation import validate_and_sanitize_user_data, sanitize_string
from app.services.base_service import BaseService


class UserService(BaseService[User]):
    """
    Service class to encapsulate business logic related to users.
    This provides a layer of abstraction between the routes and the database models.
    """

    def __init__(self, user_repository: Optional[UserRepository] = None) -> None:
        """
        Initialize the service with a repository.

        Args:
            user_repository: The repository to use.
                If not provided, a new instance will be created.
        """
        repository = user_repository or UserRepository()
        super().__init__(repository, User, validate_and_sanitize_user_data, sanitize_string)
        self.logger.debug("UserService initialized")

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get a user by its primary key ID.

        Args:
            user_id: The primary key ID of the user

        Returns:
            The user object or None if not found
        """
        self.logger.debug(f"Getting user by ID: {user_id}")
        user = super().get_by_id(user_id)
        if user:
            self.logger.debug(f"Found user with ID: {user_id}")
        else:
            self.logger.info(f"No user found with ID: {user_id}")
        return user

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by its username.

        Args:
            username: The username

        Returns:
            The user object or None if not found
        """
        self.logger.debug(f"Getting user by username: {username}")
        user = self.repository.get_by_username(username)
        if user:
            self.logger.debug(f"Found user with username: {username}")
        else:
            self.logger.debug(f"No user found with username: {username}")
        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by its email.

        Args:
            email: The email

        Returns:
            The user object or None if not found
        """
        self.logger.debug(f"Getting user by email: {email}")
        user = self.repository.get_by_email(email)
        if user:
            self.logger.debug(f"Found user with email: {email}")
        else:
            self.logger.debug(f"No user found with email: {email}")
        return user

    def create_user(self, username: str, email: str, password: str, role: str = 'user') -> User:
        """
        Create a new user.

        Args:
            username: The username
            email: The email
            password: The password
            role: The user role. Defaults to 'user'.

        Returns:
            The newly created user

        Raises:
            ValueError: If the user data is invalid
            Exception: If there's an error creating the user
        """
        # Sanitize inputs
        username = sanitize_string(username)
        email = sanitize_string(email)
        # Don't sanitize password
        role = sanitize_string(role)

        self.logger.info(f"Creating new user with username: {username}, email: {email}, role: {role}")

        # Validate user data
        user_data = {
            'username': username,
            'email': email,
            'password': password,
            'role': role
        }

        try:
            # This will validate and sanitize the data
            validated_data = validate_and_sanitize_user_data(user_data)

            # Check if user already exists
            existing_user = self.get_user_by_username(validated_data['username'])
            if existing_user:
                self.logger.warning(f"Attempted to create user with existing username: {validated_data['username']}")
                raise ValueError(f"User with username {validated_data['username']} already exists")

            existing_email = self.get_user_by_email(validated_data['email'])
            if existing_email:
                self.logger.warning(f"Attempted to create user with existing email: {validated_data['email']}")
                raise ValueError(f"User with email {validated_data['email']} already exists")

            # Create user without password
            create_data = {
                'username': validated_data['username'],
                'email': validated_data['email'],
                'role': validated_data['role']
            }

            user = self.repository.create(create_data)
            self.logger.debug(f"User created with ID: {user.id}")

            # Set password separately
            user.set_password(validated_data['password'])
            user = self.repository.update(user, {})  # Save the password hash
            self.logger.info(f"User {validated_data['username']} (ID: {user.id}, role: {validated_data['role']}) successfully created")
            return user
        except ValueError as e:
            self.logger.warning(f"Validation error creating user: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error creating user: {str(e)}")
            raise

    def update_user(self, user: User, user_data: Dict[str, Any]) -> User:
        """
        Update an existing user with the given data.

        Args:
            user: The user object to update
            user_data: Dictionary containing user attributes to update

        Returns:
            The updated user

        Raises:
            ValueError: If the user data is invalid
            Exception: If there's an error updating the user
        """
        self.logger.info(f"Updating user: {user.username} (ID: {user.id})")
        self.logger.debug(f"Update data: {user_data}")

        try:
            # Validate and sanitize the user data
            validated_data = validate_and_sanitize_user_data(user_data)
            update_data: Dict[str, Any] = {}

            # Check username uniqueness if being updated
            if 'username' in validated_data and validated_data['username'] != user.username:
                existing_user = self.get_user_by_username(validated_data['username'])
                if existing_user and existing_user.id != user.id:
                    self.logger.warning(f"Attempted to update user to existing username: {validated_data['username']}")
                    raise ValueError(f"User with username {validated_data['username']} already exists")
                update_data['username'] = validated_data['username']
                self.logger.debug(f"Updating username from {user.username} to {validated_data['username']}")

            # Check email uniqueness if being updated
            if 'email' in validated_data and validated_data['email'] != user.email:
                existing_user = self.get_user_by_email(validated_data['email'])
                if existing_user and existing_user.id != user.id:
                    self.logger.warning(f"Attempted to update user to existing email: {validated_data['email']}")
                    raise ValueError(f"User with email {validated_data['email']} already exists")
                update_data['email'] = validated_data['email']
                self.logger.debug(f"Updating email from {user.email} to {validated_data['email']}")

            # Handle role update
            if 'role' in validated_data and validated_data['role'] != user.role:
                update_data['role'] = validated_data['role']
                self.logger.debug(f"Updating role from {user.role} to {validated_data['role']}")

            # Update basic fields
            if update_data:
                user = self.repository.update(user, update_data)
                self.logger.debug(f"Updated user basic fields: {update_data.keys()}")

            # Handle password separately
            if 'password' in validated_data:
                self.logger.debug(f"Updating password for user: {user.username}")
                user.set_password(validated_data['password'])
                user = self.repository.update(user, {})  # Save the password hash
                self.logger.debug(f"Password updated for user: {user.username}")

            self.logger.info(f"User {user.username} (ID: {user.id}) successfully updated")
            return user
        except ValueError as e:
            self.logger.warning(f"Validation error updating user {user.username} (ID: {user.id}): {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error updating user {user.username} (ID: {user.id}): {str(e)}")
            raise

    def delete_user(self, user: User) -> None:
        """
        Soft delete a user by setting its deleted_at timestamp.

        Args:
            user: The user object to delete

        Raises:
            Exception: If there's an error soft deleting the user
        """
        self.logger.warning(f"Soft deleting user: {user.username} (ID: {user.id})")
        try:
            super().delete(user)
            self.logger.info(f"User {user.username} (ID: {user.id}) successfully soft deleted")
        except Exception as e:
            self.logger.error(f"Error soft deleting user {user.username} (ID: {user.id}): {str(e)}")
            raise

    def hard_delete_user(self, user: User) -> None:
        """
        Permanently delete a user from the database.
        This should be used with caution as it cannot be undone.

        Args:
            user: The user object to delete

        Raises:
            Exception: If there's an error deleting the user
        """
        self.logger.warning(f"Hard deleting user: {user.username} (ID: {user.id})")
        try:
            super().hard_delete(user)
            self.logger.info(f"User {user.username} (ID: {user.id}) successfully hard deleted")
        except Exception as e:
            self.logger.error(f"Error hard deleting user {user.username} (ID: {user.id}): {str(e)}")
            raise

    def restore_user(self, user: User) -> User:
        """
        Restore a soft-deleted user.

        Args:
            user: The user object to restore

        Returns:
            The restored user

        Raises:
            Exception: If there's an error restoring the user
        """
        self.logger.info(f"Restoring user: {user.username} (ID: {user.id})")
        try:
            restored_user = super().restore(user)
            self.logger.info(f"User {user.username} (ID: {user.id}) successfully restored")
            return restored_user
        except Exception as e:
            self.logger.error(f"Error restoring user {user.username} (ID: {user.id}): {str(e)}")
            raise

    def get_deleted_users(self) -> List[User]:
        """
        Get all soft-deleted users.

        Returns:
            List of all soft-deleted users
        """
        self.logger.debug("Getting all soft-deleted users")
        try:
            users = super().get_deleted()
            self.logger.debug(f"Retrieved {len(users)} soft-deleted users")
            return users
        except Exception as e:
            self.logger.error(f"Error retrieving soft-deleted users: {str(e)}")
            raise

    def get_all_users_including_deleted(self) -> List[User]:
        """
        Get all users including soft-deleted ones.

        Returns:
            List of all users including soft-deleted ones
        """
        self.logger.debug("Getting all users including soft-deleted")
        try:
            users = super().get_all_including_deleted()
            self.logger.debug(f"Retrieved {len(users)} users including soft-deleted")
            return users
        except Exception as e:
            self.logger.error(f"Error retrieving all users including soft-deleted: {str(e)}")
            raise

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user.

        Args:
            username: The username
            password: The password

        Returns:
            The authenticated user or None if authentication fails
        """
        # Sanitize username (don't sanitize password)
        username = sanitize_string(username)

        self.logger.info(f"Authentication attempt for user: {username}")
        try:
            # Convert username to lowercase for case-insensitive authentication
            username = username.lower() if username else username

            user = self.repository.authenticate(username, password)
            if user:
                self.logger.info(f"User {username} (ID: {user.id}) authenticated successfully")
            else:
                self.logger.warning(f"Failed authentication attempt for user: {username}")
            return user
        except Exception as e:
            self.logger.error(f"Error during authentication for user {username}: {str(e)}")
            raise

    def get_all_users(self) -> List[User]:
        """
        Get all users.

        Returns:
            List of all users
        """
        self.logger.debug("Getting all users")
        try:
            users = super().get_all()
            self.logger.debug(f"Retrieved {len(users)} users")
            return users
        except Exception as e:
            self.logger.error(f"Error retrieving all users: {str(e)}")
            raise
