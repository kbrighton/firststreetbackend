"""
Test factories for creating model instances for testing.

This module provides factory classes for creating instances of models
for testing purposes. These factories use the factory_boy library to
generate test data with sensible defaults that can be overridden as needed.
"""

import factory
from factory.faker import Faker
from datetime import datetime, date, timedelta
from app.extensions import db
from app.models.user import User
from app.models.customer import Customer
from app.models.order import Order


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Base factory class with common configuration."""
    
    class Meta:
        abstract = True
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"


class UserFactory(BaseFactory):
    """Factory for creating User instances."""
    
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    role = "user"
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)
    deleted_at = None
    
    @factory.post_generation
    def set_password(self, create, extracted, **kwargs):
        """Set the password after the user is created."""
        if not create:
            return
        
        password = extracted or "password123"
        self.set_password(password)


class CustomerFactory(BaseFactory):
    """Factory for creating Customer instances."""
    
    class Meta:
        model = Customer
    
    cust_id = factory.Sequence(lambda n: f"{n:05d}")
    customer = factory.Faker('company')
    customer_email = factory.Faker('email')
    address_line_1 = factory.Faker('street_address')
    city = factory.Faker('city')
    state = factory.Faker('state_abbr')
    zip = factory.Faker('zipcode')
    telephone_1 = factory.Faker('phone_number')
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)
    deleted_at = None


class OrderFactory(BaseFactory):
    """Factory for creating Order instances."""
    
    class Meta:
        model = Order
    
    log = factory.Sequence(lambda n: f"{n:05d}A")
    cust = factory.LazyAttribute(lambda obj: CustomerFactory().cust_id)
    title = factory.Faker('sentence', nb_words=4)
    datin = factory.LazyFunction(date.today)
    dueout = factory.LazyAttribute(lambda obj: obj.datin + timedelta(days=7))
    logtype = factory.Iterator(['TR', 'DP', 'AA', 'VG', 'DG', 'GM', 'DTF', 'PP'])
    print_n = factory.Faker('random_int', min=1, max=1000)
    colorf = factory.Faker('random_int', min=1, max=4)
    subtotal = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    sales_tax = factory.LazyAttribute(lambda obj: float(obj.subtotal) * 0.08)
    total = factory.LazyAttribute(lambda obj: float(obj.subtotal) + float(obj.sales_tax))
    rush = factory.Faker('boolean')
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)
    deleted_at = None