from app.extensions import marshmallow
from app.models import Order
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
