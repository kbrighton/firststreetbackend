# FirstStreet Backend Tests

This directory contains unit tests for the FirstStreet Backend application.

## Test Structure

The tests are organized by component type:

- `models/`: Tests for data models
  - `test_customer_model.py`: Tests for the Customer model
  - `test_order_model.py`: Tests for the Order model
  - `test_user_model.py`: Tests for the User model

- `services/`: Tests for service layer
  - `test_base_service.py`: Tests for the BaseService class
  - `test_customer_service.py`: Tests for the CustomerService class
  - `test_order_service.py`: Tests for the OrderService class
  - `test_user_service.py`: Tests for the UserService class

- `utils/`: Tests for utility functions
  - `test_validation.py`: Tests for validation utilities

- `conftest.py`: Common test fixtures and setup

## Running Tests

### Using the Test Runner Script

The easiest way to run all tests is to use the test runner script:

```bash
python run_tests.py
```

This will run all tests with verbose output.

### Using pytest Directly

You can also run tests using pytest directly:

```bash
# Run all tests
pytest app/tests

# Run tests for a specific component
pytest app/tests/models/
pytest app/tests/services/
pytest app/tests/utils/

# Run a specific test file
pytest app/tests/models/test_customer_model.py

# Run a specific test class
pytest app/tests/models/test_customer_model.py::TestCustomerModel

# Run a specific test method
pytest app/tests/models/test_customer_model.py::TestCustomerModel::test_create_valid_customer
```

## Test Coverage

The tests cover:

1. **Models**:
   - Creation and validation of model instances
   - Field validation logic
   - Event listeners for validation
   - Relationships between models
   - Soft delete functionality

2. **Services**:
   - CRUD operations
   - Business logic
   - Error handling
   - Validation and sanitization
   - Authentication (for UserService)

3. **Utilities**:
   - Input validation
   - Data sanitization
   - Security (XSS prevention)

## Adding New Tests

When adding new tests:

1. Follow the existing structure and naming conventions
2. Use the fixtures defined in `conftest.py` where appropriate
3. Ensure tests are isolated and don't depend on external resources
4. Mock external dependencies when necessary
5. Test both valid and invalid inputs
6. Test edge cases

## Test Environment

The tests use a SQLite in-memory database by default. This is configured in the `app` fixture in `conftest.py`.