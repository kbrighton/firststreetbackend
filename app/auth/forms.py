from typing import Any
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, Field
from wtforms.validators import DataRequired, Length, Regexp, ValidationError
from app.utils.form_validators import normalize_to_lowercase


class LoginForm(FlaskForm):
    """
    Form for user login.
    """

    username = StringField('Username', validators=[
        DataRequired(message="Username is required"),
        Length(min=3, max=64, message="Username must be between 3 and 64 characters"),
        Regexp(r'^[A-Za-z0-9_.\-]+$', message="Username can only contain letters, numbers, underscores, periods, and hyphens"),
        normalize_to_lowercase
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required"),
        Length(min=8, message="Password must be at least 8 characters")
    ])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
