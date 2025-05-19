# Import all schemas here to make them available when importing from app.schemas
from app.schemas.customer_schema import customer_schema, customers_schema
from app.schemas.order_schema import order_schema, orders_schema
from app.schemas.user_schema import user_schema, users_schema

# This allows imports like `from app.schemas import order_schema, orders_schema`
# while maintaining separation of schema definitions in individual files