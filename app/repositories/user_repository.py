"""
User repository module for data access operations on User entities.

This module provides a concrete implementation of the BaseRepository for User entities,
offering specific query methods tailored to user data access needs, including authentication
and lookup by username or email.
"""

from typing import Optional, Type

from app.models import User
from app.repositories.base_repository import BaseRepository, T


class UserRepository(BaseRepository[User]):
    """
    Repository for User model operations.
    Implements the BaseRepository interface for the User model.
    """

    @property
    def model(self) -> Type[User]:
        """
        The SQLAlchemy model class that this repository handles.
        """
        return User

    def get_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username.

        Args:
            username: The username to search for

        Returns:
            The user object or None if not found
        """
        return self.find_by(username=username)

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email.

        Args:
            email: The email to search for

        Returns:
            The user object or None if not found
        """
        return self.find_by(email=email)

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user with username and password.

        Args:
            username: The username
            password: The password

        Returns:
            The authenticated user or None if authentication fails
        """
        user = self.get_by_username(username)
        if user is None or not user.check_password(password):
            return None
        return user
