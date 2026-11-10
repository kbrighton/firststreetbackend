"""Backward-compatible exports for schemas defined in :mod:`app.schemas`."""

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

__all__ = [
    'CustomerSchema', 'customer_schema', 'customers_schema',
    'OrderSchema', 'order_schema', 'orders_schema',
    'UserSchema', 'user_schema', 'users_schema',
]
