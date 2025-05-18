# Utils Package

This package contains utility functions and classes used throughout the application.

## Structure

- `__init__.py`: Package initialization
- `pagination.py`: Pagination utilities for handling paginated data

## Usage

Utilities should be imported directly from their modules:

```python
from app.utils.pagination import SimplePagination
```

## Adding New Utilities

When adding new utilities:

1. Consider whether the utility is general-purpose or specific to a particular domain
2. For general-purpose utilities, create a new file or add to an existing one in this package
3. For domain-specific utilities, consider adding them to the relevant domain package
4. Ensure utilities are well-documented with docstrings
5. Consider adding tests for complex utility functions