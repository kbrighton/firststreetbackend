from .extensions import marshmallow
from .models import Order, User, Customer
from marshmallow import fields


class OrderSchema(marshmallow.SQLAlchemyAutoSchema):

    class Meta:
        model = Order
        include_relationships = True
        fields = (
        "id", "log", "cust", "title", "datin", "artout", "dueout", "print_n", "artlo", "prior", "logtype", "colorf", "rush",
        "ref_artlo", "howship", "datout", "created_at", "updated_at")
        dateformat = "%Y-%m-%d"


order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)


class CustomerSchema(marshmallow.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        #include_relationships = True
        fields = (
        "id", "cust_id", "customer_id", "customer", "address_line_1", "address_line_2", "city", "state", "zip",
        "bill_to_contact", "telephone_1", "telephone_2", "fax_number", "tax_id", "resale_no", "cust_since",
        "ship_to_1_address_line_1", "ship_to_1_address_line_2", "ship_to_1_city", "ship_to_1_state", "ship_to_1_zip",
        "customer_email", "created_at", "updated_at")
        dateformat = "%Y-%m-%d"


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)


class UserSchema(marshmallow.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        fields = ("id", "username", "email", "created_at", "updated_at")
        # Exclude password_hash for security reasons
        dateformat = "%Y-%m-%d"


user_schema = UserSchema()
users_schema = UserSchema(many=True)
