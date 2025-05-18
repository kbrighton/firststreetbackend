from app.extensions import marshmallow
from app.models import User


class UserSchema(marshmallow.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        fields = ("id", "username", "email", "created_at", "updated_at")
        # Exclude password_hash for security reasons
        dateformat = "%Y-%m-%d"


user_schema = UserSchema()
users_schema = UserSchema(many=True)
