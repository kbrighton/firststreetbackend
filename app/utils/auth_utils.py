from functools import wraps
from flask import abort
from flask_login import current_user

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