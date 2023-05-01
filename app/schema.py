from .extensions import marshmallow
from .models import Order, User, Customer


class OrderSchema(marshmallow.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        fields = (
        "LOG", "CUST", "TITLE", "DATIN", "ARTOUT", "DUEOUT", "PRINT_N", "ARTLO", "PRIOR", "LOGTYPE", "COLORF", "RUSH",
        "REF_ARTLO", "HOWSHIP", "DATOUT")
        dateformat = "%x"


order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)


class CustomerSchema(marshmallow.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)


class UserSchema(marshmallow.SQLAlchemyAutoSchema):
    class Meta:
        model = User
