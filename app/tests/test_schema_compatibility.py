from app.schema import (
    CustomerSchema as LegacyCustomerSchema,
    OrderSchema as LegacyOrderSchema,
    UserSchema as LegacyUserSchema,
    customer_schema as legacy_customer_schema,
    customers_schema as legacy_customers_schema,
    order_schema as legacy_order_schema,
    orders_schema as legacy_orders_schema,
    user_schema as legacy_user_schema,
    users_schema as legacy_users_schema,
)
from app.schemas import (
    CustomerSchema,
    OrderSchema,
    UserSchema,
    customer_schema,
    customers_schema,
    order_schema,
    orders_schema,
    user_schema,
    users_schema,
)


def test_legacy_schema_exports_are_canonical_objects():
    assert LegacyOrderSchema is OrderSchema
    assert LegacyCustomerSchema is CustomerSchema
    assert LegacyUserSchema is UserSchema
    assert legacy_order_schema is order_schema
    assert legacy_orders_schema is orders_schema
    assert legacy_customer_schema is customer_schema
    assert legacy_customers_schema is customers_schema
    assert legacy_user_schema is user_schema
    assert legacy_users_schema is users_schema


def test_order_schema_payloads_match(sample_order):
    assert legacy_order_schema.dump(sample_order) == order_schema.dump(sample_order)
    assert legacy_orders_schema.dump([sample_order]) == orders_schema.dump([sample_order])


def test_customer_schema_payloads_match(sample_customer):
    assert legacy_customer_schema.dump(sample_customer) == customer_schema.dump(sample_customer)
    assert legacy_customers_schema.dump([sample_customer]) == customers_schema.dump([sample_customer])


def test_user_schema_payloads_match(sample_user):
    assert legacy_user_schema.dump(sample_user) == user_schema.dump(sample_user)
    assert legacy_users_schema.dump([sample_user]) == users_schema.dump([sample_user])
