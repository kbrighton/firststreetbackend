from typing import Any, Optional as OptionalType, Dict, List, Union
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, DateField, IntegerField, SelectField, Field
from wtforms.validators import Length, Optional, DataRequired, ValidationError, Regexp, NumberRange
from datetime import date
from app.utils.form_validators import validate_date_not_in_past, validate_alphanumeric, validate_date_range, validate_at_least_one_field


class OrderForm(FlaskForm):
    """
    Form for creating and editing orders.
    """

    log = StringField("LOG#", validators=[
        DataRequired(message="LOG# is required"),
        Length(min=5, max=5, message="LOG# must be exactly 5 characters"),
        Regexp(r'^[A-Za-z0-9]+$', message="LOG# must contain only letters and numbers")
    ])
    cust = StringField("Customer#", validators=[
        DataRequired(message="Customer# is required"),
        Length(min=5, max=5, message="Customer# must be exactly 5 characters"),
        Regexp(r'^[A-Za-z0-9]+$', message="Customer# must contain only letters and numbers")
    ])
    title = StringField("Title", validators=[
        DataRequired(message="Title is required"),
        Length(max=100, message="Title must be less than 100 characters")
    ])
    datin = DateField("Date In", validators=[
        DataRequired(message="Date In is required")
    ])
    artout = DateField("Art Due Out", validators=[
        Optional(),
        validate_date_not_in_past
    ])
    dueout = DateField("Order Due Out", validators=[
        Optional(),
        validate_date_not_in_past
    ])
    print_n = IntegerField("Quantity", validators=[
        Optional(),
        NumberRange(min=1, message="Quantity must be a positive number")
    ])
    artlo = StringField("Art Log", validators=[
        Optional(),
        Length(max=20, message="Art Log must be less than 20 characters"),
        Regexp(r'^[A-Za-z0-9\-_]*$', message="Art Log must contain only letters, numbers, hyphens, and underscores")
    ])
    rush = BooleanField("RUSH?")
    prior = IntegerField("Priority", validators=[
        Optional(),
        NumberRange(min=1, max=10, message="Priority must be between 1 and 10")
    ])
    logtype = SelectField("Log Type",
                          choices=[("TR", "Transfer"), ("DP", "Direct Print"), ("AA", "Art Approval"), ("VG", "Vinyl"),
                                   ("DG", "Digital Graphics"), ("GM", "General Maintenance"),("DTF", "Direct to Film"),
                                   ("PP", "Promotional Products")],
                          validators=[DataRequired(message="Log Type is required")])
    colorf = IntegerField("# of Colors", validators=[
        Optional(),
        NumberRange(min=0, message="Number of colors must be a non-negative number")
    ])
    ref_artlo = StringField("Art Reference", validators=[
        Optional(),
        Length(min=5, max=5, message="Art Reference must be exactly 5 characters"),
        Regexp(r'^[A-Za-z0-9]*$', message="Art Reference must contain only letters and numbers")
    ])
    howship = IntegerField("How Shipped", validators=[
        Optional(),
        NumberRange(min=1, message="How Shipped must be a positive number")
    ])
    artno = StringField("Artist ID", validators=[
        Optional(),
        Length(min=4, max=5, message="Artist ID must be between 4 and 5 characters"),
        Regexp(r'^[A-Za-z0-9]*$', message="Artist ID must contain only letters and numbers")
    ])
    datout = DateField("DATOUT", validators=[Optional()])

    submit = SubmitField("Submit")


class SearchForm(FlaskForm):
    """
    Form for searching orders.
    """

    cust = StringField("Customer ID", validators=[
        Optional(),
        Length(max=5, message="Customer ID must be 5 characters or less"),
        Regexp(r'^[A-Za-z0-9]*$', message="Customer ID must contain only letters and numbers")
    ])
    title = StringField("Title", validators=[
        Optional(),
        Length(max=100, message="Title must be less than 100 characters")
    ])
    submit = SubmitField("Submit")

    def validate(self, extra_validators: OptionalType[Dict[str, List[Any]]] = None) -> bool:
        """
        Validate the form.

        Args:
            extra_validators: Additional validators to apply.

        Returns:
            True if the form is valid, False otherwise.
        """
        if not super(SearchForm, self).validate(extra_validators=extra_validators):
            return False

        # Validate that at least one search field has a value
        if not validate_at_least_one_field(self, ['cust', 'title'], 'At least one search field is required'):
            return False

        return True


class SearchLog(FlaskForm):
    """
    Form for searching orders by log number.
    """

    log = StringField("LOG #", validators=[
        DataRequired(message="LOG # is required"),
        Length(min=5, max=5, message="LOG # must be exactly 5 characters"),
        Regexp(r'^[A-Za-z0-9]+$', message="LOG # must contain only letters and numbers")
    ])
    submit = SubmitField("Submit")


class DisplayDueouts(FlaskForm):
    """
    Form for displaying orders due out within a date range.
    """

    start_date = DateField("Start Due Outs Date", validators=[
        DataRequired(message="Start date is required")
    ])
    end_date = DateField("End Due Outs Date", validators=[
        DataRequired(message="End date is required"),
        validate_date_range
    ])
    submit = SubmitField("Submit")
