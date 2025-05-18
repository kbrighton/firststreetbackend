"""
Custom exceptions for the application.

This module defines custom exception classes that can be raised by the application
to indicate specific error conditions. These exceptions are caught by the error
handlers in app/errors/handlers.py and converted to appropriate HTTP responses.
"""


class BaseAppException(Exception):
    """Base exception class for all application-specific exceptions."""
    status_code = 500
    message = "An unexpected error occurred."

    def __init__(self, message=None, status_code=None, payload=None):
        """Initialize the exception with optional custom message and status code."""
        super().__init__(message or self.message)
        self.message = message or self.message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        """Convert the exception to a dictionary for JSON responses."""
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status'] = self.status_code
        return rv


class ResourceNotFoundError(BaseAppException):
    """Exception raised when a requested resource is not found."""
    status_code = 404
    message = "The requested resource was not found."


class ValidationError(BaseAppException):
    """Exception raised when input validation fails."""
    status_code = 400
    message = "Invalid input data."


class AuthenticationError(BaseAppException):
    """Exception raised when authentication fails."""
    status_code = 401
    message = "Authentication failed."


class AuthorizationError(BaseAppException):
    """Exception raised when a user is not authorized to perform an action."""
    status_code = 403
    message = "You do not have permission to perform this action."


class DatabaseError(BaseAppException):
    """Exception raised when a database operation fails."""
    status_code = 500
    message = "A database error occurred."