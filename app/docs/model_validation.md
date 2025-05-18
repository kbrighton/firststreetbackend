# Model-Level Validation

This document describes the implementation of data validation at the model level in the FirstStreet application.

## Overview

Data validation has been implemented at the model level for all major models in the application:
- Customer
- Order
- User

The validation ensures that data meets specific requirements before it's saved to the database, helping to maintain data integrity and prevent invalid data from being stored.

## Implementation Details

### Validation Approach

The validation is implemented using SQLAlchemy event listeners that trigger before insert and update operations. Each model has:

1. A `validate_data()` method that checks the model's attributes and returns a dictionary of validation errors.
2. Static validation methods for specific validation types (e.g., alphanumeric, length, email, etc.).
3. Event listeners that call the validation method before insert and update operations.

### Customer Model Validation

The Customer model validates:
- Customer ID (must be exactly 5 alphanumeric characters)
- Customer name (must be between 1 and 255 characters)
- Email (must be a valid email format)
- ZIP code (must be a valid ZIP code format)
- Phone numbers (must be valid phone number formats)

### Order Model Validation

The Order model validates:
- Log number (must be between 5 and 7 alphanumeric characters)
- Customer ID (must be exactly 5 alphanumeric characters)
- Title (must be between 1 and 256 characters)
- Art-related fields (must follow specific formats)
- Numeric fields (must be non-negative)
- Log type (must be one of the valid types)
- Dates (future dates where appropriate)
- Date ranges (end dates must be after start dates)

### User Model Validation

The User model validates:
- Username (must be between 3 and 64 characters and contain only allowed characters)
- Email (must be a valid email format)
- Role (must be one of the valid roles)

## Usage

The validation happens automatically when models are saved to the database. If validation fails, a `ValueError` is raised with details about the validation errors.

Example:
```python
try:
    customer = Customer(cust_id="123")  # Invalid (too short)
    db.session.add(customer)
    db.session.commit()
except ValueError as e:
    print(f"Validation error: {str(e)}")
    db.session.rollback()
```

## Testing

A test script is available at `app/tests/test_model_validation.py` that tests the validation for all models. It includes tests for:
- Validating valid and invalid model instances
- Testing database-level validation through event listeners

Run the tests with:
```
python app/tests/test_model_validation.py
```