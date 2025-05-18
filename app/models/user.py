from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import re
from typing import Dict, Optional
from datetime import datetime

from app.extensions import db, login
from sqlalchemy import event


"""
User model representing user accounts in the system.

This module defines the User model which stores information about user accounts,
including authentication details, roles, and timestamps.
It also provides methods for password management and data validation.
"""


class User(UserMixin, db.Model):
    """
    User model for storing user account information.

    This class represents a user account in the system and contains all the fields
    necessary for authentication and authorization, including username, email,
    password hash, and role.

    Attributes:
        id (int): Primary key for the user.
        username (str): Unique username for the user.
        email (str): Unique email address for the user.
        password_hash (str): Hashed password for the user.
        role (str): Role of the user (e.g., 'user', 'admin').
        created_at (datetime): Timestamp when the record was created.
        updated_at (datetime): Timestamp when the record was last updated.
        deleted_at (datetime): Timestamp when the record was soft-deleted, or None if active.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='user')  # Possible values: 'user', 'admin'
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), 
                          onupdate=db.func.current_timestamp())
    deleted_at = db.Column(db.DateTime, nullable=True)

    def set_password(self, password: str) -> None:
        """
        Set the user's password by generating a password hash.

        Args:
            password: The plain text password to hash and store.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """
        Check if the provided password matches the stored hash.

        Args:
            password: The plain text password to check.

        Returns:
            True if the password matches, False otherwise.
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        """
        Return a string representation of the User object.

        Returns:
            str: String representation of the User.
        """
        return f'<User {self.username}>'

    def validate_data(self) -> Dict[str, str]:
        """
        Validate the user data against business rules.

        This method checks various fields of the user for validity, including:
        - Username format and length
        - Email format
        - Role validity

        Returns:
            Dict[str, str]: A dictionary mapping field names to error messages if validation fails,
                           or an empty dictionary if all validations pass.
        """
        errors = {}

        # Validate username
        if self.username:
            if not self._validate_length(self.username, 3, 64):
                errors['username'] = "Username must be between 3 and 64 characters"
            elif not re.match(r'^[A-Za-z0-9_.\-]+$', self.username):
                errors['username'] = "Username can only contain letters, numbers, underscores, periods, and hyphens"
        else:
            errors['username'] = "Username is required"

        # Validate email
        if self.email:
            if not self._validate_email(self.email):
                errors['email'] = "Invalid email format"
        else:
            errors['email'] = "Email is required"

        # Validate role
        if self.role:
            valid_roles = ['user', 'admin']
            if self.role not in valid_roles:
                errors['role'] = f"Role must be one of: {', '.join(valid_roles)}"

        return errors

    @staticmethod
    def _validate_length(value: str, min_length: int = 0, max_length: Optional[int] = None) -> bool:
        """
        Validate that a string's length is within the specified range.

        Args:
            value (str): The string to validate.
            min_length (int, optional): The minimum allowed length. Defaults to 0.
            max_length (Optional[int], optional): The maximum allowed length. Defaults to None.

        Returns:
            bool: True if the string length is valid, False otherwise.
        """
        if value is None:
            return min_length == 0

        length = len(value)

        if length < min_length:
            return False

        if max_length is not None and length > max_length:
            return False

        return True

    @staticmethod
    def _validate_email(value: str) -> bool:
        """
        Validate email format.

        Args:
            value (str): The email address to validate.

        Returns:
            bool: True if the email format is valid, False if it's invalid or empty.
        """
        if not value:
            return False

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, value))


@event.listens_for(User, 'before_insert')
@event.listens_for(User, 'before_update')
def validate_user(mapper, connection, user):
    """
    Validate user data before insert or update operations.

    This function is registered as an event listener for both 'before_insert' and 'before_update'
    events on the User model. It calls the validate_data method on the user instance and
    raises a ValueError if any validation errors are found.

    Args:
        mapper: The SQLAlchemy mapper that is the target of this event.
        connection: The SQLAlchemy connection being used for the operation.
        user (User): The user instance being inserted or updated.

    Raises:
        ValueError: If validation fails, with a message containing all validation errors.
    """
    errors = user.validate_data()
    if errors:
        error_messages = "; ".join([f"{field}: {message}" for field, message in errors.items()])
        raise ValueError(f"User validation failed: {error_messages}")


@login.user_loader
def load_user(id: str) -> Optional[User]:
    """
    Load a user from the database for Flask-Login.

    This function is used by Flask-Login to load a user from the database
    based on the user ID stored in the session.

    Args:
        id: The user ID as a string.

    Returns:
        The user object if found, or None if not found.
    """
    from app.repositories.user_repository import UserRepository
    user_repository = UserRepository()
    return user_repository.get_by_id(int(id))
