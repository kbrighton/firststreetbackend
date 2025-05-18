"""
Tests for the factory fixtures.

This module demonstrates how to use the factory fixtures to create test data.
It serves as an example for other developers on how to use the factories effectively.
"""

import pytest
from app.models.user import User
from app.models.customer import Customer
from app.models.order import Order


def test_user_factory(user_factory, db_session):
    """Test that the user factory creates valid User instances."""
    # Create a user with default values
    user1 = user_factory()
    assert isinstance(user1, User)
    assert user1.id is not None
    assert user1.username.startswith('user')
    assert user1.email.endswith('@example.com')
    assert user1.role == 'user'
    assert user1.check_password('password123')
    
    # Create a user with custom values
    user2 = user_factory(username='custom_user', email='custom@example.com', role='admin')
    assert user2.username == 'custom_user'
    assert user2.email == 'custom@example.com'
    assert user2.role == 'admin'
    
    # Create a user with a custom password
    user3 = user_factory(set_password='custom_password')
    assert user3.check_password('custom_password')
    
    # Verify users are in the database
    users = db_session.query(User).all()
    assert len(users) >= 3


def test_customer_factory(customer_factory, db_session):
    """Test that the customer factory creates valid Customer instances."""
    # Create a customer with default values
    customer1 = customer_factory()
    assert isinstance(customer1, Customer)
    assert customer1.id is not None
    assert len(customer1.cust_id) == 5
    assert customer1.customer is not None
    assert '@' in customer1.customer_email
    
    # Create a customer with custom values
    customer2 = customer_factory(
        cust_id='54321',
        customer='Custom Company',
        customer_email='custom@example.com',
        zip='90210'
    )
    assert customer2.cust_id == '54321'
    assert customer2.customer == 'Custom Company'
    assert customer2.customer_email == 'custom@example.com'
    assert customer2.zip == '90210'
    
    # Verify customers are in the database
    customers = db_session.query(Customer).all()
    assert len(customers) >= 2


def test_order_factory(order_factory, customer_factory, db_session):
    """Test that the order factory creates valid Order instances."""
    # Create an order with auto-created customer
    order1 = order_factory()
    assert isinstance(order1, Order)
    assert order1.id is not None
    assert len(order1.log) >= 5
    assert order1.cust is not None
    assert order1.title is not None
    assert order1.datin is not None
    assert order1.dueout is not None
    assert order1.logtype in ['TR', 'DP', 'AA', 'VG', 'DG', 'GM', 'DTF', 'PP']
    
    # Create an order with a specific customer
    customer = customer_factory(cust_id='98765')
    order2 = order_factory(customer=customer, title='Custom Order', logtype='TR')
    assert order2.cust == '98765'
    assert order2.title == 'Custom Order'
    assert order2.logtype == 'TR'
    
    # Create an order with custom values
    order3 = order_factory(
        log='ABCDE',
        title='Another Order',
        print_n=500,
        colorf=3,
        subtotal=1000.0,
        total=1080.0
    )
    assert order3.log == 'ABCDE'
    assert order3.title == 'Another Order'
    assert order3.print_n == 500
    assert order3.colorf == 3
    assert order3.subtotal == 1000.0
    assert order3.total == 1080.0
    
    # Verify orders are in the database
    orders = db_session.query(Order).all()
    assert len(orders) >= 3


def test_factory_relationships(order_factory, db_session):
    """Test that the factories maintain proper relationships between models."""
    # Create an order, which should create a customer
    order = order_factory(title='Relationship Test')
    
    # Verify the order has a valid customer reference
    assert order.cust is not None
    
    # Retrieve the customer from the database
    customer = db_session.query(Customer).filter_by(cust_id=order.cust).first()
    assert customer is not None
    
    # Verify the relationship works through the ORM
    assert order.customer is not None
    assert order.customer.cust_id == customer.cust_id