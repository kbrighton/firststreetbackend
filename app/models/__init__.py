# Import all models here to make them available when importing from app.models
from app.models.customer import Customer
from app.models.order import Order
from app.models.user import User

# This allows imports like `from app.models import Customer, Order, User`
# while maintaining separation of model definitions in individual files