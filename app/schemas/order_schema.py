from app.extensions import marshmallow
from app.models import Order
from marshmallow import fields


class OrderSchema(marshmallow.SQLAlchemyAutoSchema):
    # Include customer data in the schema
    customer_name = fields.Method("get_customer_name")

    def get_customer_name(self, obj):
        """Get the customer name from the related customer object"""
        if obj.customer:
            return obj.customer.customer
        return None

    class Meta:
        model = Order
        include_relationships = True
        fields = (
        "id", "log", "cust", "customer_name", "title", "datin", "artout", "dueout", "print_n", "artlo", "prior", "logtype", "colorf", "rush",
        "ref_artlo", "howship", "datout", "created_at", "updated_at")
        dateformat = "%x"


order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
