# Models Package

This package contains the SQLAlchemy model definitions for the application's database tables.

## Structure

- `__init__.py`: Imports and exposes all models
- `customer.py`: Customer model definition
- `order.py`: Order model definition
- `user.py`: User model definition and authentication-related functionality

## Usage

Models should be imported from the package, not from individual files:

```python
from app.models import Customer, Order, User
```

This ensures that the models are properly registered with SQLAlchemy and maintains backward compatibility with existing code.

## Adding New Models

When adding a new model:

1. Create a new file named after the model (e.g., `product.py` for a Product model)
2. Define the model class in that file
3. Import the model in `__init__.py` to make it available when importing from the package