import pytest
from app.utils.validation import (
    sanitize_string,
    validate_alphanumeric,
    validate_length,
    validate_date_not_in_past,
    validate_date_range,
    validate_number_range,
    validate_and_sanitize_order_data,
    validate_and_sanitize_customer_data,
    validate_and_sanitize_user_data
)
from datetime import date, timedelta


class TestValidationUtils:
    """Test suite for validation utility functions."""

    def test_sanitize_string(self):
        """Test sanitizing strings."""
        # Test normal string
        assert sanitize_string("test") == "test"
        
        # Test string with HTML
        assert sanitize_string("<script>alert('XSS')</script>") == "&lt;script&gt;alert('XSS')&lt;/script&gt;"
        
        # Test string with leading/trailing whitespace
        assert sanitize_string("  test  ") == "test"
        
        # Test None value
        assert sanitize_string(None) is None

    def test_validate_alphanumeric(self):
        """Test validating alphanumeric strings."""
        # Valid alphanumeric strings
        assert validate_alphanumeric("abc123") is True
        assert validate_alphanumeric("ABC123") is True
        assert validate_alphanumeric("123") is True
        
        # Invalid strings
        assert validate_alphanumeric("abc-123") is False
        assert validate_alphanumeric("abc 123") is False
        assert validate_alphanumeric("abc_123") is False
        assert validate_alphanumeric("") is False
        assert validate_alphanumeric(None) is False
        
        # Test allow_empty parameter
        assert validate_alphanumeric("", allow_empty=True) is True
        assert validate_alphanumeric(None, allow_empty=True) is True

    def test_validate_length(self):
        """Test validating string length."""
        # Valid lengths
        assert validate_length("12345", 5, 5) is True
        assert validate_length("12345", 1, 10) is True
        assert validate_length("", 0) is True
        
        # Invalid lengths
        assert validate_length("1234", 5, 5) is False
        assert validate_length("123456", 5, 5) is False
        assert validate_length("", 1) is False
        assert validate_length("12345", 0, 4) is False
        
        # Test with None
        assert validate_length(None, 0) is True
        assert validate_length(None, 1) is False

    def test_validate_date_not_in_past(self):
        """Test validating that a date is not in the past."""
        today = date.today()
        tomorrow = today + timedelta(days=1)
        yesterday = today - timedelta(days=1)
        
        # Valid dates
        assert validate_date_not_in_past(today) is True
        assert validate_date_not_in_past(tomorrow) is True
        assert validate_date_not_in_past(None) is True
        
        # Invalid dates
        assert validate_date_not_in_past(yesterday) is False

    def test_validate_date_range(self):
        """Test validating date ranges."""
        today = date.today()
        tomorrow = today + timedelta(days=1)
        yesterday = today - timedelta(days=1)
        
        # Valid ranges
        assert validate_date_range(today, today) is True
        assert validate_date_range(today, tomorrow) is True
        assert validate_date_range(None, today) is True
        assert validate_date_range(today, None) is True
        assert validate_date_range(None, None) is True
        
        # Invalid ranges
        assert validate_date_range(tomorrow, today) is False
        assert validate_date_range(today, yesterday) is False

    def test_validate_number_range(self):
        """Test validating number ranges."""
        # Valid ranges
        assert validate_number_range(5, 0) is True
        assert validate_number_range(5, 5) is True
        assert validate_number_range(5, 0, 10) is True
        assert validate_number_range(None) is True
        
        # Invalid ranges
        assert validate_number_range(5, 6) is False
        assert validate_number_range(5, 0, 4) is False

    def test_validate_and_sanitize_order_data_valid(self):
        """Test validating and sanitizing valid order data."""
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        valid_data = {
            "log": "12345",
            "cust": "12345",
            "title": "Test Order",
            "datin": today,
            "dueout": tomorrow,
            "logtype": "TR",
            "print_n": 100,
            "colorf": 2,
            "subtotal": 500.0,
            "total": 550.0
        }
        
        sanitized_data = validate_and_sanitize_order_data(valid_data)
        
        assert sanitized_data["log"] == "12345"
        assert sanitized_data["cust"] == "12345"
        assert sanitized_data["title"] == "Test Order"
        assert sanitized_data["datin"] == today
        assert sanitized_data["dueout"] == tomorrow
        assert sanitized_data["logtype"] == "TR"
        assert sanitized_data["print_n"] == 100
        assert sanitized_data["colorf"] == 2
        assert sanitized_data["subtotal"] == 500.0
        assert sanitized_data["total"] == 550.0

    def test_validate_and_sanitize_order_data_invalid(self):
        """Test validating and sanitizing invalid order data."""
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        invalid_data = {
            "log": "123",  # Too short
            "cust": "123",  # Too short
            "title": "",    # Empty title
            "datin": today,
            "dueout": yesterday,  # Due date in past
            "logtype": "INVALID",  # Invalid log type
            "print_n": -1,  # Negative quantity
            "colorf": -2,   # Negative colors
            "subtotal": -500.0,  # Negative subtotal
            "total": -550.0  # Negative total
        }
        
        with pytest.raises(ValueError):
            validate_and_sanitize_order_data(invalid_data)

    def test_validate_and_sanitize_customer_data_valid(self):
        """Test validating and sanitizing valid customer data."""
        valid_data = {
            "cust_id": "12345",
            "name": "Test Customer",
            "email": "test@example.com",
            "zip": "12345",
            "phone": "123-456-7890"
        }
        
        sanitized_data = validate_and_sanitize_customer_data(valid_data)
        
        assert sanitized_data["cust_id"] == "12345"
        assert sanitized_data["name"] == "Test Customer"
        assert sanitized_data["email"] == "test@example.com"
        assert sanitized_data["zip"] == "12345"
        assert sanitized_data["phone"] == "123-456-7890"

    def test_validate_and_sanitize_customer_data_invalid(self):
        """Test validating and sanitizing invalid customer data."""
        invalid_data = {
            "cust_id": "123",  # Too short
            "name": "",        # Empty name
        }
        
        with pytest.raises(ValueError):
            validate_and_sanitize_customer_data(invalid_data)

    def test_validate_and_sanitize_user_data_valid(self):
        """Test validating and sanitizing valid user data."""
        valid_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "role": "user"
        }
        
        sanitized_data = validate_and_sanitize_user_data(valid_data)
        
        assert sanitized_data["username"] == "testuser"
        assert sanitized_data["email"] == "test@example.com"
        assert sanitized_data["password"] == "password123"  # Password should not be sanitized
        assert sanitized_data["role"] == "user"

    def test_validate_and_sanitize_user_data_invalid(self):
        """Test validating and sanitizing invalid user data."""
        invalid_data = {
            "username": "t@",  # Invalid characters
            "email": "invalid-email",  # Invalid email
            "password": "pass",  # Too short
            "role": "superadmin"  # Invalid role
        }
        
        with pytest.raises(ValueError):
            validate_and_sanitize_user_data(invalid_data)

    def test_sanitize_html_injection(self):
        """Test that HTML injection is properly sanitized."""
        html_injection = "<script>alert('XSS')</script>"
        sanitized = sanitize_string(html_injection)
        
        assert "<script>" not in sanitized
        assert "&lt;script&gt;" in sanitized
        assert sanitized == "&lt;script&gt;alert('XSS')&lt;/script&gt;"

    def test_validate_and_sanitize_order_data_with_html_injection(self):
        """Test that HTML injection in order data is properly sanitized."""
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        data_with_injection = {
            "log": "12345",
            "cust": "12345",
            "title": "<script>alert('XSS')</script>",
            "datin": today,
            "dueout": tomorrow,
            "logtype": "TR"
        }
        
        sanitized_data = validate_and_sanitize_order_data(data_with_injection)
        
        assert sanitized_data["title"] == "&lt;script&gt;alert('XSS')&lt;/script&gt;"