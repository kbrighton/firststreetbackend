import pytest
from app.models.customer import Customer
from app.extensions import db
from sqlalchemy.exc import IntegrityError


class TestCustomerModel:
    """Test suite for the Customer model."""

    def test_create_valid_customer(self, db_session, valid_customer_data):
        """Test creating a valid customer."""
        customer = Customer(**valid_customer_data)
        db_session.add(customer)
        db_session.commit()

        assert customer.id is not None
        assert customer.cust_id == valid_customer_data['cust_id']
        assert customer.customer == valid_customer_data['customer']
        assert customer.customer_email == valid_customer_data['customer_email']
        assert customer.zip == valid_customer_data['zip']
        assert customer.telephone_1 == valid_customer_data['telephone_1']
        assert customer.created_at is not None
        assert customer.updated_at is not None
        assert customer.deleted_at is None

    def test_customer_representation(self, sample_customer):
        """Test the string representation of a customer."""
        assert str(sample_customer) == f'<Customer "{sample_customer.customer}">'
        assert repr(sample_customer) == f'<Customer "{sample_customer.customer}">'

    def test_validate_data_valid_customer(self, sample_customer):
        """Test validate_data with a valid customer."""
        errors = sample_customer.validate_data()
        assert errors == {}

    def test_validate_data_invalid_customer(self, db_session, invalid_customer_data):
        """Test validate_data with an invalid customer."""
        customer = Customer(**invalid_customer_data)
        errors = customer.validate_data()

        assert 'cust_id' in errors
        assert 'customer' in errors
        assert 'customer_email' in errors
        assert 'zip' in errors
        assert 'telephone_1' in errors

    def test_validate_customer_event_listener(self, db_session, invalid_customer_data):
        """Test that the validate_customer event listener prevents invalid customers from being saved."""
        customer = Customer(**invalid_customer_data)
        db_session.add(customer)

        with pytest.raises(ValueError) as excinfo:
            db_session.commit()

        assert "Customer validation failed" in str(excinfo.value)
        db_session.rollback()

    def test_unique_cust_id_constraint(self, db_session, valid_customer_data):
        """Test that cust_id must be unique."""
        # Create first customer
        customer1 = Customer(**valid_customer_data)
        db_session.add(customer1)
        db_session.commit()

        # Try to create second customer with same cust_id
        customer2 = Customer(**valid_customer_data)
        db_session.add(customer2)

        with pytest.raises(IntegrityError):
            db_session.commit()

        db_session.rollback()

    def test_validate_alphanumeric(self):
        """Test the _validate_alphanumeric method."""
        assert Customer._validate_alphanumeric("ABC123") is True
        assert Customer._validate_alphanumeric("ABC-123") is False
        assert Customer._validate_alphanumeric("") is False
        assert Customer._validate_alphanumeric("", allow_empty=True) is True
        assert Customer._validate_alphanumeric(None) is False
        assert Customer._validate_alphanumeric(None, allow_empty=True) is True

    def test_validate_length(self):
        """Test the _validate_length method."""
        assert Customer._validate_length("12345", 5, 5) is True
        assert Customer._validate_length("1234", 5, 5) is False
        assert Customer._validate_length("123456", 5, 5) is False
        assert Customer._validate_length("12345", 1, 10) is True
        assert Customer._validate_length("", 0) is True
        assert Customer._validate_length("", 1) is False
        assert Customer._validate_length(None, 0) is True
        assert Customer._validate_length(None, 1) is False

    def test_validate_email(self):
        """Test the _validate_email method."""
        assert Customer._validate_email("test@example.com") is True
        assert Customer._validate_email("invalid-email") is False
        assert Customer._validate_email("") is True
        assert Customer._validate_email(None) is True

    def test_validate_zip(self):
        """Test the _validate_zip method."""
        assert Customer._validate_zip("12345") is True
        assert Customer._validate_zip("12345-6789") is True
        assert Customer._validate_zip("1234") is False
        assert Customer._validate_zip("123456") is False
        assert Customer._validate_zip("12345-678") is False
        assert Customer._validate_zip("abcde") is False
        assert Customer._validate_zip("") is True
        assert Customer._validate_zip(None) is True

    def test_validate_phone(self):
        """Test the _validate_phone method."""
        assert Customer._validate_phone("1234567890") is True
        assert Customer._validate_phone("123-456-7890") is True
        assert Customer._validate_phone("(123) 456-7890") is True
        assert Customer._validate_phone("123.456.7890") is True
        assert Customer._validate_phone("11234567890") is True  # With country code
        assert Customer._validate_phone("123") is False
        assert Customer._validate_phone("abcdefghij") is False
        assert Customer._validate_phone("") is True
        assert Customer._validate_phone(None) is True

    def test_soft_delete(self, db_session, sample_customer):
        """Test soft deleting a customer."""
        # Set deleted_at timestamp
        sample_customer.deleted_at = db.func.current_timestamp()
        db_session.commit()

        # Verify customer is soft deleted
        assert sample_customer.deleted_at is not None

        # Verify customer is not returned in normal queries
        from app.repositories.customer_repository import CustomerRepository
        repo = CustomerRepository()
        customers = repo.get_all()
        assert sample_customer not in customers

        # Verify customer is returned in queries that include deleted
        deleted_customers = repo.get_deleted()
        assert sample_customer in deleted_customers
