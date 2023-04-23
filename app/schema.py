from .extensions import db,marshmallow
from .models import Order,User,Customer


class OrderSchema(marshmallow.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        fields = ("LOG", "CUST", "TITLE", "DATIN", "ARTOUT", "DUEOUT", "PRINT_N", "ARTLO", "PRIOR", "LOGTYPE", "COLORF", "REF_ARTLO", "HOWSHIP", "DATOUT")


order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)


class CustomerSchema(marshmallow.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer


class UserSchema(marshmallow.SQLAlchemyAutoSchema):
    class Meta:
        model = User

