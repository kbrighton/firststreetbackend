from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, \
    SubmitField, DateField, IntegerField
from wtforms.validators import DataRequired, Length, Email, Regexp
from wtforms import ValidationError
from wtforms.widgets import TextInput


class OrderForm(FlaskForm):
    LOG = StringField("LOG#")
    CUST = StringField("Customer#")
    TITLE= StringField("Title")
    DATIN = DateField("Date In")
    ARTOUT = DateField("Art Due Out")
    DUEOUT = DateField("Order Due Out")
    PRINT_N = IntegerField("Quantity")
    ARTLO = StringField("Art Log")
    RUSH = BooleanField("RUSH?")
    PRIOR = IntegerField("Priority")
    LOGTYPE=StringField("Log Type")
    COLORF = IntegerField("# of Colors")
    REF_ARTLO = StringField("Art Reference")

    Submit = SubmitField("Submit")


class SearchForm(FlaskForm):
    CUST = StringField("Customer ID")
    TITLE = StringField("Title")
    Submit = SubmitField("Submit")

