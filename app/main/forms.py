from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, DateField, IntegerField, SelectField
from wtforms.validators import Length, Optional


class OrderForm(FlaskForm):
    LOG = StringField("LOG#", validators=[Length(min=5, max=5)])
    CUST = StringField("Customer#", validators=[Length(min=5, max=5)])
    TITLE = StringField("Title")
    DATIN = DateField("Date In")
    ARTOUT = DateField("Art Due Out", validators=[Optional()])
    DUEOUT = DateField("Order Due Out", validators=[Optional()])
    PRINT_N = IntegerField("Quantity", validators=[Optional()])
    ARTLO = StringField("Art Log", validators=[Optional()])
    RUSH = BooleanField("RUSH?")
    PRIOR = IntegerField("Priority", validators=[Optional()])
    LOGTYPE = SelectField("Log Type",
                          choices=[("TR", "Transfer"), ("DP", "Direct Print"), ("AA", "Art Approval"), ("VG", "Vinyl"),
                                   ("DG", "Digital Graphics"), ("GM", "General Maintenance"),("DTF", "Direct to Film"),
                                   ("PP", "Promotional Products")])
    COLORF = IntegerField("# of Colors", validators=[Optional()])
    REF_ARTLO = StringField("Art Reference", validators=[Optional(), Length(min=5, max=5)])
    HOWSHIP = IntegerField("How Shipped", validators=[Optional()])
    DATOUT = DateField("DATOUT", validators=[Optional()])

    Submit = SubmitField("Submit")


class SearchForm(FlaskForm):
    CUST = StringField("Customer ID")
    TITLE = StringField("Title")
    Submit = SubmitField("Submit")


class SearchLog(FlaskForm):
    LOG = StringField("LOG #")
    Submit = SubmitField("Submit")


class DisplayDueouts(FlaskForm):
    StartDate = DateField("Start Due Outs Date")
    EndDate = DateField("End Due Outs Date")
    Submit = SubmitField("Submit")
