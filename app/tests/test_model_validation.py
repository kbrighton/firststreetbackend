"""
Test script for model-level validation.

This script tests the validation implemented in the Customer, Order, and User models.
"""
import sys
import os
from datetime import date, timedelta

# Add the repository root to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app import create_app
from app.extensions import db
from app.models.customer import Customer
from app.models.order import Order
from app.models.user import User

# Create a test app
app = create_app('testing')

# Test validation in Customer model
def test_customer_validation():
    print("\nTesting Customer validation...")

    with app.app_context():
        # Test valid customer
        valid_customer = Customer(
            cust_id="12345",
            customer="Test Customer",
            customer_email="test@example.com",
            zip="12345",
            telephone_1="123-456-7890"
        )

        try:
            # Validate without saving to DB
            errors = valid_customer.validate_data()
            if errors:
                print(f"Unexpected validation errors for valid customer: {errors}")
            else:
                print("Valid customer passed validation as expected")
        except Exception as e:
            print(f"Error validating valid customer: {str(e)}")

        # Test invalid customer
        invalid_customer = Customer(
            cust_id="123",  # Too short
            customer="",    # Empty name
            customer_email="invalid-email",  # Invalid email
            zip="abc",      # Invalid zip
            telephone_1="123"  # Invalid phone
        )

        try:
            # Validate without saving to DB
            errors = invalid_customer.validate_data()
            if errors:
                print(f"Validation errors for invalid customer (expected): {errors}")
            else:
                print("ERROR: Invalid customer passed validation unexpectedly")
        except Exception as e:
            print(f"Error validating invalid customer: {str(e)}")

# Test validation in Order model
def test_order_validation():
    print("\nTesting Order validation...")

    with app.app_context():
        # Test valid order
        today = date.today()
        tomorrow = today + timedelta(days=1)

        valid_order = Order(
            log="12345",
            cust="12345",
            title="Test Order",
            datin=today,
            dueout=tomorrow,
            logtype="TR",
            print_n=100,
            colorf=2,
            subtotal=500.0,
            total=550.0
        )

        try:
            # Validate without saving to DB
            errors = valid_order.validate_data()
            if errors:
                print(f"Unexpected validation errors for valid order: {errors}")
            else:
                print("Valid order passed validation as expected")
        except Exception as e:
            print(f"Error validating valid order: {str(e)}")

        # Test invalid order
        yesterday = today - timedelta(days=1)

        invalid_order = Order(
            log="123",  # Too short
            cust="123",  # Too short
            title="",    # Empty title
            datin=today,
            dueout=yesterday,  # Due date in past
            logtype="INVALID",  # Invalid log type
            print_n=-1,  # Negative quantity
            colorf=-2,   # Negative colors
            subtotal=-500.0,  # Negative subtotal
            total=-550.0  # Negative total
        )

        try:
            # Validate without saving to DB
            errors = invalid_order.validate_data()
            if errors:
                print(f"Validation errors for invalid order (expected): {errors}")
            else:
                print("ERROR: Invalid order passed validation unexpectedly")
        except Exception as e:
            print(f"Error validating invalid order: {str(e)}")

# Test validation in User model
def test_user_validation():
    print("\nTesting User validation...")

    with app.app_context():
        # Test valid user
        valid_user = User(
            username="testuser",
            email="test@example.com",
            role="user"
        )

        try:
            # Validate without saving to DB
            errors = valid_user.validate_data()
            if errors:
                print(f"Unexpected validation errors for valid user: {errors}")
            else:
                print("Valid user passed validation as expected")
        except Exception as e:
            print(f"Error validating valid user: {str(e)}")

        # Test invalid user
        invalid_user = User(
            username="t@",  # Invalid characters
            email="invalid-email",  # Invalid email
            role="superadmin"  # Invalid role
        )

        try:
            # Validate without saving to DB
            errors = invalid_user.validate_data()
            if errors:
                print(f"Validation errors for invalid user (expected): {errors}")
            else:
                print("ERROR: Invalid user passed validation unexpectedly")
        except Exception as e:
            print(f"Error validating invalid user: {str(e)}")

# Test DB-level validation (event listeners)
def test_db_validation():
    print("\nTesting database-level validation...")

    with app.app_context():
        # Create a test database session
        db.create_all()

        # Test adding invalid customer to DB
        invalid_customer = Customer(
            cust_id="123",  # Too short
            customer="Test Customer"
        )

        try:
            db.session.add(invalid_customer)
            db.session.commit()
            print("ERROR: Invalid customer was added to database")
        except Exception as e:
            print(f"Validation prevented invalid customer from being added (expected): {str(e)}")
            db.session.rollback()

        # Test adding valid customer to DB
        valid_customer = Customer(
            cust_id="12345",
            customer="Test Customer"
        )

        try:
            db.session.add(valid_customer)
            db.session.commit()
            print("Valid customer was added to database as expected")

            # Clean up
            db.session.delete(valid_customer)
            db.session.commit()
        except Exception as e:
            print(f"Error adding valid customer to database: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    test_customer_validation()
    test_order_validation()
    test_user_validation()
    test_db_validation()
    print("\nAll tests completed.")
