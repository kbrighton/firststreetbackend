# Error Handling System

This document describes the error handling system implemented in the application.

## Overview

The application has a comprehensive error handling system that:

1. Provides user-friendly error pages for web requests
2. Returns structured JSON responses for API requests
3. Logs all errors for monitoring and debugging
4. Includes custom exception classes for application-specific errors

## Error Pages

The application includes custom error pages for common HTTP error codes:

- 400 Bad Request
- 403 Forbidden
- 404 Not Found
- 405 Method Not Allowed
- 500 Internal Server Error

These pages provide a consistent user experience and include a link to return to the home page.

## Custom Exceptions

The application defines several custom exception classes in `app/errors/exceptions.py`:

### BaseAppException

Base class for all application-specific exceptions. It includes:

- A default status code (500)
- A default message
- Support for custom messages, status codes, and additional payload data
- A `to_dict()` method for converting the exception to a dictionary for JSON responses

### Specific Exception Classes

- **ResourceNotFoundError**: For when a requested resource is not found (404)
- **ValidationError**: For input validation failures (400)
- **AuthenticationError**: For authentication failures (401)
- **AuthorizationError**: For authorization failures (403)
- **DatabaseError**: For database operation failures (500)

## Using Custom Exceptions

### Raising Exceptions

```python
from app.errors.exceptions import ResourceNotFoundError, ValidationError

# Example: Raise a ResourceNotFoundError when a user is not found
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        raise ResourceNotFoundError(f"User with ID {user_id} not found")
    return user

# Example: Raise a ValidationError when input validation fails
def create_user(data):
    if not data.get('username'):
        raise ValidationError("Username is required")
    # ... rest of the function
```

### Exception Handling

The application automatically handles these exceptions:

- For web requests: Renders the appropriate error template
- For API requests: Returns a JSON response with the error details

## Testing Error Handling

You can test the error handling system using:

1. **Unit Tests**: Run `python -m unittest test_error_handlers.py`
2. **Manual Testing**: Run `python test_error_app.py` and visit:
   - http://localhost:5001/404 (Not Found)
   - http://localhost:5001/500 (Server Error)
   - http://localhost:5001/403 (Forbidden)
   - http://localhost:5001/400 (Bad Request)
   - http://localhost:5001/405 (Method Not Allowed - send a POST request)
   - http://localhost:5001/custom/resource-not-found (Custom ResourceNotFoundError)
   - http://localhost:5001/custom/validation-error (Custom ValidationError)
   - http://localhost:5001/custom/authorization-error (Custom AuthorizationError)
   - http://localhost:5001/custom/database-error (Custom DatabaseError)
   - http://localhost:5001/api/resource-not-found (API ResourceNotFoundError - returns JSON)
   - http://localhost:5001/api/validation-error (API ValidationError - returns JSON)

## Logging

All errors are logged using Flask's built-in logger:

- 400, 403, 404, 405 errors are logged at WARNING level
- 500 errors and custom exceptions are logged at ERROR level

The logs include details such as the URL, HTTP method, and error message to help with debugging.