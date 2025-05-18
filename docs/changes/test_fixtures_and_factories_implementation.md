# Test Fixtures and Factories Implementation

## Overview

This document describes the implementation of test fixtures and factories for the FirstStreet Backend application. Test fixtures and factories provide a standardized way to create test data, making tests more maintainable and easier to write.

## Changes Made

1. Created a `factories.py` file in the `app/tests` directory with factory classes for the following models:
   - `UserFactory`: For creating User instances
   - `CustomerFactory`: For creating Customer instances
   - `OrderFactory`: For creating Order instances

2. Updated `conftest.py` to include factory-based fixtures:
   - `user_factory`: For creating User instances
   - `customer_factory`: For creating Customer instances
   - `order_factory`: For creating Order instances with optional customer relationships

3. Created a `test_factories.py` file with example tests demonstrating how to use the factories

4. Added `factory-boy` to `requirements.txt`

## How to Use the Factories

### Basic Usage

The factory fixtures return functions that can be used to create model instances with customizable attributes:

```python
def test_example(user_factory, customer_factory, order_factory):
    # Create a user with default values
    user = user_factory()
    
    # Create a customer with custom values
    customer = customer_factory(
        cust_id='12345',
        customer='Test Company',
        customer_email='test@example.com'
    )
    
    # Create an order linked to the customer
    order = order_factory(
        customer=customer,
        title='Test Order',
        logtype='TR'
    )
    
    # Assertions...
```

### Factory Features

1. **Default Values**: Factories provide sensible defaults for all required fields.

2. **Custom Values**: You can override any default value by passing it as a keyword argument.

3. **Relationships**: The `order_factory` automatically creates a customer if one isn't provided.

4. **Sequences**: Fields like `username` and `cust_id` use sequences to ensure uniqueness.

5. **Faker Integration**: Many fields use Faker to generate realistic test data.

## Benefits

1. **Reduced Boilerplate**: Less code needed to set up test data.

2. **Consistency**: Standardized approach to creating test data.

3. **Flexibility**: Easy to customize test data for specific test cases.

4. **Maintainability**: Changes to model requirements only need to be updated in one place.

## Next Steps

1. Consider creating factories for any additional models that may be added in the future.

2. Extend the factories with additional customization options as needed.

3. Use the factories in all tests that require model instances.