"""
Form utilities module.

This module provides utility functions for working with forms,
such as extracting form data to model data.
"""

from typing import Dict, Any, Optional, List


def extract_form_data(form: Any, exclude_fields: Optional[List[str]] = None, model: Optional[Any] = None) -> Dict[str, Any]:
    """
    Extract data from a form into a dictionary.

    This function extracts data from a form into a dictionary that can be used
    to create or update a model. It excludes specified fields and only includes
    fields that exist on the model (if provided).

    Args:
        form: The form to extract data from
        exclude_fields: List of field names to exclude (default: ['csrf_token', 'submit'])
        model: Optional model to check field existence against

    Returns:
        Dictionary containing form data
    """
    if exclude_fields is None:
        exclude_fields = ['csrf_token', 'submit']

    data: Dict[str, Any] = {}
    for field_name in form._fields:
        # Skip excluded fields
        if field_name in exclude_fields:
            continue

        # Skip fields that don't exist on the model (if model is provided)
        if model is not None and not hasattr(model, field_name):
            continue

        # Get the field value
        data[field_name] = getattr(form, field_name).data

    return data