import pytest
from app.models.order import Order
from app.extensions import db
from sqlalchemy.exc import IntegrityError
from datetime import date, timedelta


class TestOrderModel:
    """Test suite for the Order model."""

    def test_create_valid_order(self, db_session, valid_order_data, sample_customer):
        """Test creating a valid order."""
        order = Order(**valid_order_data)
        db_session.add(order)
        db_session.commit()

        assert order.id is not None
        assert order.log == valid_order_data['log']
        assert order.cust == valid_order_data['cust']
        assert order.title == valid_order_data['title']
        assert order.datin == valid_order_data['datin']
        assert order.dueout == valid_order_data['dueout']
        assert order.logtype == valid_order_data['logtype']
        assert order.print_n == valid_order_data['print_n']
        assert order.colorf == valid_order_data['colorf']
        assert order.subtotal == valid_order_data['subtotal']
        assert order.total == valid_order_data['total']
        assert order.created_at is not None
        assert order.updated_at is not None
        assert order.deleted_at is None

    def test_order_representation(self, sample_order):
        """Test the string representation of an order."""
        assert str(sample_order) == f'<Order "{sample_order.log}">'
        assert repr(sample_order) == f'<Order "{sample_order.log}">'

    def test_validate_data_valid_order(self, sample_order):
        """Test validate_data with a valid order."""
        errors = sample_order.validate_data()
        assert errors == {}

    def test_validate_data_invalid_order(self, db_session, invalid_order_data):
        """Test validate_data with an invalid order."""
        order = Order(**invalid_order_data)
        errors = order.validate_data()
        
        assert 'log' in errors
        assert 'cust' in errors
        assert 'title' in errors
        assert 'dueout' in errors
        assert 'logtype' in errors
        assert 'print_n' in errors
        assert 'colorf' in errors
        assert 'subtotal' in errors
        assert 'total' in errors

    def test_validate_order_event_listener(self, db_session, invalid_order_data):
        """Test that the validate_order event listener prevents invalid orders from being saved."""
        order = Order(**invalid_order_data)
        db_session.add(order)
        
        with pytest.raises(ValueError) as excinfo:
            db_session.commit()
        
        assert "Order validation failed" in str(excinfo.value)
        db_session.rollback()

    def test_unique_log_constraint(self, db_session, valid_order_data, sample_customer):
        """Test that log must be unique."""
        # Create first order
        order1 = Order(**valid_order_data)
        db_session.add(order1)
        db_session.commit()
        
        # Try to create second order with same log
        order2 = Order(**valid_order_data)
        db_session.add(order2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        db_session.rollback()

    def test_validate_alphanumeric(self):
        """Test the _validate_alphanumeric method."""
        assert Order._validate_alphanumeric("ABC123") is True
        assert Order._validate_alphanumeric("ABC-123") is False
        assert Order._validate_alphanumeric("") is False
        assert Order._validate_alphanumeric("", allow_empty=True) is True
        assert Order._validate_alphanumeric(None) is False
        assert Order._validate_alphanumeric(None, allow_empty=True) is True

    def test_validate_length(self):
        """Test the _validate_length method."""
        assert Order._validate_length("12345", 5, 5) is True
        assert Order._validate_length("1234", 5, 5) is False
        assert Order._validate_length("123456", 5, 5) is False
        assert Order._validate_length("12345", 1, 10) is True
        assert Order._validate_length("", 0) is True
        assert Order._validate_length("", 1) is False
        assert Order._validate_length(None, 0) is True
        assert Order._validate_length(None, 1) is False

    def test_validate_number_range(self):
        """Test the _validate_number_range method."""
        assert Order._validate_number_range(5, 0) is True
        assert Order._validate_number_range(0, 0) is True
        assert Order._validate_number_range(-1, 0) is False
        assert Order._validate_number_range(5, 1, 10) is True
        assert Order._validate_number_range(0, 1, 10) is False
        assert Order._validate_number_range(11, 1, 10) is False
        assert Order._validate_number_range(None) is True

    def test_validate_date_not_in_past(self):
        """Test the _validate_date_not_in_past method."""
        today = date.today()
        tomorrow = today + timedelta(days=1)
        yesterday = today - timedelta(days=1)
        
        assert Order._validate_date_not_in_past(today) is True
        assert Order._validate_date_not_in_past(tomorrow) is True
        assert Order._validate_date_not_in_past(yesterday) is False
        assert Order._validate_date_not_in_past(None) is True

    def test_validate_date_range(self):
        """Test the _validate_date_range method."""
        today = date.today()
        tomorrow = today + timedelta(days=1)
        yesterday = today - timedelta(days=1)
        
        assert Order._validate_date_range(today, today) is True
        assert Order._validate_date_range(today, tomorrow) is True
        assert Order._validate_date_range(tomorrow, today) is False
        assert Order._validate_date_range(None, today) is True
        assert Order._validate_date_range(today, None) is True
        assert Order._validate_date_range(None, None) is True

    def test_customer_relationship(self, sample_order, sample_customer):
        """Test the relationship between Order and Customer."""
        assert sample_order.customer is not None
        assert sample_order.customer.cust_id == sample_customer.cust_id
        assert sample_order.cust == sample_customer.cust_id

    def test_soft_delete(self, db_session, sample_order):
        """Test soft deleting an order."""
        # Set deleted_at timestamp
        sample_order.deleted_at = db.func.current_timestamp()
        db_session.commit()
        
        # Verify order is soft deleted
        assert sample_order.deleted_at is not None
        
        # Verify order is not returned in normal queries
        from app.repositories.order_repository import OrderRepository
        repo = OrderRepository()
        orders = repo.get_all()
        assert sample_order not in orders
        
        # Verify order is returned in queries that include deleted
        deleted_orders = repo.get_deleted()
        assert sample_order in deleted_orders