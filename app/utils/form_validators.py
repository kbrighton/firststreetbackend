"""
Form validation utilities module.

This module provides reusable form validation functions that can be used
across different form classes to reduce code duplication and ensure
consistent validation behavior.
"""

from typing import Any, Optional
from datetime import date
from wtforms import Field
from wtforms.validators import ValidationError


def validate_date_not_in_past(form: Any, field: Field) -> None:
    """
    Validate that a date field is not in the past.

    Args:
        form: The form containing the field
        field: The field to validate

    Raises:
        ValidationError: If the date is in the past
    """
    if field.data and field.data < date.today():
        raise ValidationError('Date cannot be in the past')


def validate_date_range(form: Any, field: Field) -> None:
    """
    Validate that the end date is after the start date.

    This validator should be applied to the end date field, and assumes
    that the form has a start_date field.

    Args:
        form: The form containing the field
        field: The field to validate (end date)

    Raises:
        ValidationError: If the end date is before the start date
    """
    if form.start_date.data and field.data and form.start_date.data > field.data:
        raise ValidationError('End date must be after start date')


def validate_alphanumeric(form: Any, field: Field) -> None:
    """
    Validate that a field contains only alphanumeric characters.

    Args:
        form: The form containing the field
        field: The field to validate

    Raises:
        ValidationError: If the field contains non-alphanumeric characters
    """
    if field.data and not field.data.isalnum():
        raise ValidationError('Field must contain only letters and numbers')


def normalize_to_lowercase(form: Any, field: Field) -> None:
    """
    Normalize a field value to lowercase.

    Args:
        form: The form containing the field
        field: The field to normalize

    Returns:
        None. The field value is converted to lowercase in-place.
    """
    if field.data:
        field.data = field.data.lower()


def validate_at_least_one_field(form: Any, fields: list[str], message: Optional[str] = None) -> bool:
    """
    Validate that at least one of the specified fields has a value.

    This function should be called from a form's validate method.

    Args:
        form: The form to validate
        fields: List of field names to check
        message: Custom error message (optional)

    Returns:
        True if at least one field has a value, False otherwise

    Side Effects:
        Adds an error to the first field in the list if validation fails
    """
    if not any(getattr(form, field).data for field in fields):
        error_msg = message or 'At least one field is required'
        getattr(form, fields[0]).errors.append(error_msg)
        return False
    return True