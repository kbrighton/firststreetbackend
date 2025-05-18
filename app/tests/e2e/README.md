# End-to-End Tests

This directory contains end-to-end tests for the FirstStreet Backend application. These tests verify critical user flows through the web UI, ensuring that the application works correctly from the user's perspective.

## Test Structure

The end-to-end tests are organized into the following files:

- `helpers.py`: Utility functions for common operations in end-to-end tests
- `test_auth_flows.py`: Tests for authentication flows (login, logout)
- `test_order_flows.py`: Tests for order management flows (create, edit, view)
- `test_search_flows.py`: Tests for search functionality (by customer, title, log)
- `test_complete_user_journey.py`: Comprehensive tests that simulate complete user journeys

## Running the Tests

To run all end-to-end tests:

```bash
pytest app/tests/e2e
```

To run a specific test file:

```bash
pytest app/tests/e2e/test_auth_flows.py
```

To run a specific test:

```bash
pytest app/tests/e2e/test_auth_flows.py::TestAuthFlows::test_login_success
```

## Test Coverage

The end-to-end tests cover the following critical user flows:

### Authentication Flows
- Login with valid credentials
- Login with invalid credentials
- Logout
- Remember me functionality

### Order Management Flows
- Creating a new order
- Editing an existing order
- Viewing a non-existent order (error handling)
- Viewing all due-outs
- Viewing due-outs within a date range

### Search Functionality
- Searching for orders by customer
- Searching for orders by title
- Searching for orders by log number
- Handling searches with no results
- Handling searches for non-existent log numbers

### Complete User Journey
- A comprehensive test that simulates a user going through multiple flows in a single session

## Dependencies

The end-to-end tests depend on the following:

- pytest: Testing framework
- Flask test client: For making HTTP requests to the application
- BeautifulSoup: For parsing HTML responses

## Adding New Tests

When adding new end-to-end tests:

1. Determine which user flow you want to test
2. Add the test to the appropriate test file, or create a new file if needed
3. Use the helper functions in `helpers.py` for common operations
4. Ensure your test is properly documented with docstrings
5. Run the test to verify it works correctly