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


class OrderDetailSchema(OrderSchema):
    artno = fields.String(allow_none=True)
    created_at = fields.DateTime(format='iso', allow_none=True)
    updated_at = fields.DateTime(format='iso', allow_none=True)
    created_by_username = fields.Function(
        lambda order: order.created_by.username if order.created_by else None,
        allow_none=True,
    )
    updated_by_username = fields.Function(
        lambda order: order.updated_by.username if order.updated_by else None,
        allow_none=True,
    )

    class Meta(OrderSchema.Meta):
        fields = OrderSchema.Meta.fields + (
            "artno", "created_by_username", "updated_by_username",
        )


order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
order_detail_schema = OrderDetailSchema()
