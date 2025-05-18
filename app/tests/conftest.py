import pytest
from app import create_app
from app.extensions import db
from app.models.customer import Customer
from app.models.order import Order
from app.models.user import User
from datetime import date, datetime, timedelta
from app.tests.factories import UserFactory, CustomerFactory, OrderFactory


@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = create_app('testing')

    # Create a test database and tables
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()


@pytest.fixture
def app_context(app):
    """An application context for the tests."""
    with app.app_context():
        yield


@pytest.fixture
def db_session(app_context):
    """A database session for the tests."""
    connection = db.engine.connect()
    transaction = connection.begin()

    session = db.session

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def valid_customer_data():
    """Valid customer data for tests."""
    return {
        'cust_id': '12345',
        'customer': 'Test Customer',
        'customer_email': 'test@example.com',
        'zip': '12345',
        'telephone_1': '123-456-7890'
    }


@pytest.fixture
def invalid_customer_data():
    """Invalid customer data for tests."""
    return {
        'cust_id': '123',  # Too short
        'customer': '',    # Empty name
        'customer_email': 'invalid-email',  # Invalid email
        'zip': 'abc',      # Invalid zip
        'telephone_1': '123'  # Invalid phone
    }


@pytest.fixture
def valid_order_data():
    """Valid order data for tests."""
    today = date.today()
    tomorrow = today + timedelta(days=1)

    return {
        'log': '12345',
        'cust': '12345',
        'title': 'Test Order',
        'datin': today,
        'dueout': tomorrow,
        'logtype': 'TR',
        'print_n': 100,
        'colorf': 2,
        'subtotal': 500.0,
        'total': 550.0
    }


@pytest.fixture
def invalid_order_data():
    """Invalid order data for tests."""
    today = date.today()
    yesterday = today - timedelta(days=1)

    return {
        'log': '123',  # Too short
        'cust': '123',  # Too short
        'title': '',    # Empty title
        'datin': today,
        'dueout': yesterday,  # Due date in past
        'logtype': 'INVALID',  # Invalid log type
        'print_n': -1,  # Negative quantity
        'colorf': -2,   # Negative colors
        'subtotal': -500.0,  # Negative subtotal
        'total': -550.0  # Negative total
    }


@pytest.fixture
def valid_user_data():
    """Valid user data for tests."""
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123',
        'role': 'user'
    }


@pytest.fixture
def invalid_user_data():
    """Invalid user data for tests."""
    return {
        'username': 't@',  # Invalid characters
        'email': 'invalid-email',  # Invalid email
        'password': 'pass',  # Too short
        'role': 'superadmin'  # Invalid role
    }


@pytest.fixture
def sample_customer(db_session, valid_customer_data):
    """Create a sample customer for tests using direct model instantiation."""
    customer = Customer(**valid_customer_data)
    db_session.add(customer)
    db_session.commit()
    return customer


@pytest.fixture
def sample_order(db_session, valid_order_data, sample_customer):
    """Create a sample order for tests using direct model instantiation."""
    order = Order(**valid_order_data)
    db_session.add(order)
    db_session.commit()
    return order


@pytest.fixture
def sample_user(db_session, valid_user_data):
    """Create a sample user for tests using direct model instantiation."""
    user = User(
        username=valid_user_data['username'],
        email=valid_user_data['email'],
        role=valid_user_data['role']
    )
    user.set_password(valid_user_data['password'])
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def user_factory(db_session):
    """Factory fixture for creating User instances."""
    def _user_factory(**kwargs):
        with db_session.begin_nested():
            user = UserFactory(**kwargs)
            db_session.flush()
            return user
    return _user_factory


@pytest.fixture
def customer_factory(db_session):
    """Factory fixture for creating Customer instances."""
    def _customer_factory(**kwargs):
        with db_session.begin_nested():
            customer = CustomerFactory(**kwargs)
            db_session.flush()
            return customer
    return _customer_factory


@pytest.fixture
def order_factory(db_session, customer_factory):
    """Factory fixture for creating Order instances."""
    def _order_factory(customer=None, **kwargs):
        if customer:
            kwargs['cust'] = customer.cust_id
        elif 'cust' not in kwargs:
            # Create a customer if one wasn't provided
            customer = customer_factory()
            kwargs['cust'] = customer.cust_id

        with db_session.begin_nested():
            order = OrderFactory(**kwargs)
            db_session.flush()
            return order
    return _order_factory
