"""
Utility functions for input validation and sanitization.
"""
import re
import html
from datetime import date
from typing import Any, Dict, List, Optional, Union


def sanitize_string(value: str) -> str:
    """
    Sanitize a string input to prevent XSS attacks.

    Args:
        value: The string to sanitize

    Returns:
        The sanitized string
    """
    if value is None:
        return None

    # Escape HTML special characters
    return html.escape(str(value).strip())


def validate_alphanumeric(value: str, allow_empty: bool = False) -> bool:
    """
    Validate that a string contains only alphanumeric characters.

    Args:
        value: The string to validate
        allow_empty: Whether to allow empty strings

    Returns:
        True if valid, False otherwise
    """
    if value is None or value == "":
        return allow_empty

    return bool(re.match(r'^[A-Za-z0-9]+$', value))


def validate_length(value: str, min_length: int = 0, max_length: Optional[int] = None) -> bool:
    """
    Validate that a string's length is within the specified range.

    Args:
        value: The string to validate
        min_length: The minimum allowed length
        max_length: The maximum allowed length (or None for no maximum)

    Returns:
        True if valid, False otherwise
    """
    if value is None:
        return min_length == 0

    length = len(value)

    if length < min_length:
        return False

    if max_length is not None and length > max_length:
        return False

    return True


def validate_date_not_in_past(value: date) -> bool:
    """
    Validate that a date is not in the past.

    Args:
        value: The date to validate

    Returns:
        True if valid, False otherwise
    """
    if value is None:
        return True

    return value >= date.today()


def validate_date_range(start_date: date, end_date: date) -> bool:
    """
    Validate that the end date is after the start date.

    Args:
        start_date: The start date
        end_date: The end date

    Returns:
        True if valid, False otherwise
    """
    if start_date is None or end_date is None:
        return True

    return end_date >= start_date


def validate_number_range(value: int, min_value: Optional[int] = None, max_value: Optional[int] = None) -> bool:
    """
    Validate that a number is within the specified range.

    Args:
        value: The number to validate
        min_value: The minimum allowed value (or None for no minimum)
        max_value: The maximum allowed value (or None for no maximum)

    Returns:
        True if valid, False otherwise
    """
    if value is None:
        return True

    if min_value is not None and value < min_value:
        return False

    if max_value is not None and value > max_value:
        return False

    return True


def validate_and_sanitize_order_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and sanitize order data.

    Args:
        data: The order data to validate and sanitize

    Returns:
        The validated and sanitized data

    Raises:
        ValueError: If the data is invalid
    """
    errors = []
    sanitized_data = {}

    # Validate and sanitize log
    if 'log' in data:
        log = data['log']
        if not validate_alphanumeric(log) or not validate_length(log, 5, 5):
            errors.append("LOG# must be exactly 5 alphanumeric characters")
        else:
            sanitized_data['log'] = sanitize_string(log)

    # Validate and sanitize cust
    if 'cust' in data:
        cust = data['cust']
        if not validate_alphanumeric(cust) or not validate_length(cust, 5, 5):
            errors.append("Customer# must be exactly 5 alphanumeric characters")
        else:
            sanitized_data['cust'] = sanitize_string(cust)

    # Validate and sanitize title
    if 'title' in data:
        title = data['title']
        if not validate_length(title, 1, 100):
            errors.append("Title must be between 1 and 100 characters")
        else:
            sanitized_data['title'] = sanitize_string(title)

    # Validate and sanitize artlo
    if 'artlo' in data:
        artlo = data['artlo']
        if artlo and not re.match(r'^[A-Za-z0-9\-_]*$', artlo) or not validate_length(artlo, 0, 20):
            errors.append("Art Log must contain only letters, numbers, hyphens, and underscores, and be less than 20 characters")
        else:
            sanitized_data['artlo'] = sanitize_string(artlo) if artlo else None

    # Validate and sanitize ref_artlo
    if 'ref_artlo' in data:
        ref_artlo = data['ref_artlo']
        if ref_artlo and (not validate_alphanumeric(ref_artlo, True) or not validate_length(ref_artlo, 0, 5) or (ref_artlo and len(ref_artlo) != 5)):
            errors.append("Art Reference must be exactly 5 alphanumeric characters or empty")
        else:
            sanitized_data['ref_artlo'] = sanitize_string(ref_artlo) if ref_artlo else None

    # Validate and sanitize artno
    if 'artno' in data:
        artno = data['artno']
        if artno and (not validate_alphanumeric(artno, True) or not validate_length(artno, 0, 5) or (artno and len(artno) < 4)):
            errors.append("Artist ID must be between 4 and 5 alphanumeric characters or empty")
        else:
            sanitized_data['artno'] = sanitize_string(artno) if artno else None

    # Validate and sanitize print_n
    if 'print_n' in data:
        print_n = data['print_n']
        if print_n is not None and not validate_number_range(print_n, 1):
            errors.append("Quantity must be a positive number")
        else:
            sanitized_data['print_n'] = print_n

    # Validate and sanitize prior
    if 'prior' in data:
        prior = data['prior']
        if prior is not None and not validate_number_range(prior, 1, 10):
            errors.append("Priority must be between 1 and 10")
        else:
            sanitized_data['prior'] = prior

    # Validate and sanitize colorf
    if 'colorf' in data:
        colorf = data['colorf']
        if colorf is not None and not validate_number_range(colorf, 0):
            errors.append("Number of colors must be a non-negative number")
        else:
            sanitized_data['colorf'] = colorf

    # Validate and sanitize howship
    if 'howship' in data:
        howship = data['howship']
        if howship is not None and not validate_number_range(howship, 1):
            errors.append("How Shipped must be a positive number")
        else:
            sanitized_data['howship'] = howship

    # Validate and sanitize logtype
    if 'logtype' in data:
        logtype = data['logtype']
        valid_logtypes = ["TR", "DP", "AA", "VG", "DG", "GM", "DTF", "PP"]
        if logtype not in valid_logtypes:
            errors.append(f"Log Type must be one of: {', '.join(valid_logtypes)}")
        else:
            sanitized_data['logtype'] = logtype

    # Validate and sanitize dates
    for date_field in ['datin', 'artout', 'dueout', 'datout']:
        if date_field in data:
            date_value = data[date_field]
            # Convert string dates to date objects
            if date_value and isinstance(date_value, str):
                try:
                    from datetime import datetime
                    date_value = datetime.strptime(date_value, '%Y-%m-%d').date()
                except ValueError:
                    errors.append(f"Invalid {date_field} format. Expected format: YYYY-MM-DD")
                    continue

            if date_field in ['artout', 'dueout'] and date_value and not validate_date_not_in_past(date_value):
                errors.append(f"{date_field.capitalize()} cannot be in the past")
            else:
                sanitized_data[date_field] = date_value

    # Validate and sanitize rush
    if 'rush' in data:
        sanitized_data['rush'] = bool(data['rush'])

    if errors:
        raise ValueError(", ".join(errors))

    return sanitized_data


def validate_and_sanitize_customer_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and sanitize customer data.

    Args:
        data: The customer data to validate and sanitize

    Returns:
        The validated and sanitized data

    Raises:
        ValueError: If the data is invalid
    """
    errors = []
    sanitized_data = {}

    # Validate and sanitize cust_id
    if 'cust_id' in data:
        cust_id = data['cust_id']
        if not validate_alphanumeric(cust_id) or not validate_length(cust_id, 5, 5):
            errors.append("Customer ID must be exactly 5 alphanumeric characters")
        else:
            sanitized_data['cust_id'] = sanitize_string(cust_id)

    # Validate and sanitize name
    if 'name' in data:
        name = data['name']
        if not validate_length(name, 1, 100):
            errors.append("Name must be between 1 and 100 characters")
        else:
            sanitized_data['name'] = sanitize_string(name)

    # Validate and sanitize other fields
    for field in ['address', 'city', 'state', 'zip', 'phone', 'email', 'contact']:
        if field in data:
            value = data[field]
            if value is not None:
                sanitized_data[field] = sanitize_string(value)

    if errors:
        raise ValueError(", ".join(errors))

    return sanitized_data


def validate_and_sanitize_user_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and sanitize user data.

    Args:
        data: The user data to validate and sanitize

    Returns:
        The validated and sanitized data

    Raises:
        ValueError: If the data is invalid
    """
    errors = []
    sanitized_data = {}

    # Validate and sanitize username
    if 'username' in data:
        username = data['username']
        if not validate_length(username, 3, 64) or not re.match(r'^[A-Za-z0-9_.\-]+$', username):
            errors.append("Username must be between 3 and 64 characters and can only contain letters, numbers, underscores, periods, and hyphens")
        else:
            sanitized_data['username'] = sanitize_string(username).lower()

    # Validate and sanitize password
    if 'password' in data:
        password = data['password']
        if not validate_length(password, 8):
            errors.append("Password must be at least 8 characters")
        else:
            sanitized_data['password'] = password  # Don't sanitize passwords

    # Validate and sanitize role
    if 'role' in data:
        role = data['role']
        valid_roles = ['user', 'admin']
        if role not in valid_roles:
            errors.append(f"Role must be one of: {', '.join(valid_roles)}")
        else:
            sanitized_data['role'] = role

    if errors:
        raise ValueError(", ".join(errors))

    return sanitized_data
