# Authorization Implementation

## Overview
This document describes the implementation of proper authorization checks for all routes in the application. The implementation includes:

1. Adding a role field to the User model
2. Creating authorization decorators
3. Applying authorization checks to routes
4. Updating the UserService to handle roles

## Changes Made

### 1. User Model
Added a `role` field to the User model with possible values 'user' and 'admin'. The default role is 'user'.

```python
class User(UserMixin, db.Model):
    # ... existing fields ...
    role = db.Column(db.String(20), default='user')  # Possible values: 'user', 'admin'
    # ... existing fields ...
```

### 2. Authorization Decorators
Created two decorators in `app/utils/auth_utils.py`:

1. `role_required(role)`: A general decorator that checks if the current user has a specific role or one of a list of roles.
2. `admin_required`: A specific decorator that restricts access to admin users only.

```python
def role_required(role):
    """
    Decorator to restrict access to users with a specific role.
    
    Args:
        role (str or list): The role or list of roles required to access the route.
        
    Returns:
        function: The decorated function.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)  # Unauthorized
            
            # Check if the user has the required role
            if isinstance(role, list):
                if current_user.role not in role:
                    abort(403)  # Forbidden
            else:
                if current_user.role != role:
                    abort(403)  # Forbidden
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """
    Decorator to restrict access to admin users only.
    
    Returns:
        function: The decorated function.
    """
    return role_required('admin')(f)
```

### 3. Route Authorization
Applied the `admin_required` decorator to user management routes in the API blueprint:

- `get_users`: List all users (admin only)
- `get_user`: Get a specific user (admin only)
- `create_user`: Create a new user (admin only)
- `delete_user`: Delete a user (admin only)

For the `update_user` route, implemented a special check that allows users to update their own information, but only admins can update other users' information or change roles:

```python
@bp.route('/users/<int:id>', methods=['PUT'])
@login_required
def update_user(id):
    """Update an existing user (admin only or self)."""
    # Check if user is updating themselves or is admin
    if id != current_user.id and current_user.role != 'admin':
        abort(403, description="You can only update your own user information unless you're an admin")

    # ... existing code ...

    # Only admins can change roles
    if 'role' in data and current_user.role != 'admin':
        abort(403, description="Only admins can change user roles")

    # ... existing code ...
```

### 4. UserService Updates
Updated the UserService to handle the role parameter:

- Added a `role` parameter to the `create_user` method with a default value of 'user'
- Added validation to ensure the role is either 'user' or 'admin'
- Updated the `update_user` method to handle updating the role

### 5. Database Migration
Created and applied a database migration to add the role field to the User table in the database.

## Usage
To restrict a route to admin users only, apply both the `@login_required` and `@admin_required` decorators:

```python
@bp.route('/admin-only-route')
@login_required
@admin_required
def admin_only_route():
    # Only admin users can access this route
    pass
```

To restrict a route to users with a specific role, use the `@role_required` decorator:

```python
@bp.route('/specific-role-route')
@login_required
@role_required('specific_role')
def specific_role_route():
    # Only users with the 'specific_role' role can access this route
    pass
```

## Future Improvements
1. Add more granular permissions beyond just 'user' and 'admin' roles
2. Implement role-based UI elements (hiding buttons/links for unauthorized actions)
3. Add audit logging for authorization-related events
4. Consider implementing a permission system rather than just roles for more flexibility