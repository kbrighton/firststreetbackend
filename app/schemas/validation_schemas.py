import re

from marshmallow import EXCLUDE, Schema, ValidationError, fields, pre_load, validates_schema, validate

from app.models import User
from app.utils.form_validators import is_valid_date_range

LOG_TYPES = ('TR', 'DP', 'AA', 'VG', 'DG', 'GM', 'DTF', 'PP')


def _not_blank(message):
    def validator(value):
        if value is None or not value.strip():
            raise ValidationError(message)

    return validator


def _is_blank(value):
    return isinstance(value, str) and not value.strip()


def _validate_email(value):
    if not User._validate_email(value):
        raise ValidationError('Invalid email format')


def _search_length(max_length, message):
    def validator(value):
        if value is not None and value.strip() and len(value) > max_length:
            raise ValidationError(message)

    return validator


def _search_alphanumeric(value):
    if value is not None and value.strip() and not re.fullmatch(r'[A-Za-z0-9]*', value):
        raise ValidationError('Customer ID must contain only letters and numbers')


def _as_dict(data):
    if isinstance(data, dict):
        return data.copy()
    if hasattr(data, 'to_dict'):
        return data.to_dict()
    return data


class FormInteger(fields.Integer):
    def __init__(self, range_error=None, **kwargs):
        self.range_error = range_error
        super().__init__(**kwargs)

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return super()._deserialize(value, attr, data, **kwargs)
        except ValidationError as error:
            if not self.range_error:
                raise
            messages = error.messages
            if isinstance(messages, str):
                messages = [messages]
            if isinstance(messages, list):
                raise ValidationError(messages + [self.range_error])
            raise


class OrderLoadSchema(Schema):
    log = fields.String(
        required=True,
        error_messages={'required': 'LOG# is required', 'null': 'LOG# is required'},
        validate=[
            _not_blank('LOG# is required'),
            validate.Length(min=5, max=5, error='LOG# must be exactly 5 characters'),
            validate.Regexp(r'^[A-Za-z0-9]+$', error='LOG# must contain only letters and numbers'),
        ],
    )
    cust = fields.String(
        required=True,
        error_messages={'required': 'Customer# is required', 'null': 'Customer# is required'},
        validate=[
            _not_blank('Customer# is required'),
            validate.Length(min=5, max=5, error='Customer# must be exactly 5 characters'),
            validate.Regexp(r'^[A-Za-z0-9]+$', error='Customer# must contain only letters and numbers'),
        ],
    )
    title = fields.String(
        required=True,
        error_messages={'required': 'Title is required', 'null': 'Title is required'},
        validate=[
            _not_blank('Title is required'),
            validate.Length(max=100, error='Title must be less than 100 characters'),
        ],
    )
    datin = fields.Date(
        required=True,
        error_messages={
            'required': 'Date In is required',
            'null': 'Date In is required',
            'invalid': 'Not a valid date value.',
        },
    )
    artout = fields.Date(allow_none=True, error_messages={'invalid': 'Not a valid date value.'})
    dueout = fields.Date(allow_none=True, error_messages={'invalid': 'Not a valid date value.'})
    print_n = FormInteger(
        range_error='Quantity must be a positive number',
        allow_none=True,
        error_messages={'invalid': 'Not a valid integer value.'},
        validate=validate.Range(min=1, error='Quantity must be a positive number'),
    )
    artlo = fields.String(
        allow_none=True,
        validate=[
            validate.Length(max=20, error='Art Log must be less than 20 characters'),
            validate.Regexp(
                r'^[A-Za-z0-9\-_]*$',
                error='Art Log must contain only letters, numbers, hyphens, and underscores',
            ),
        ],
    )
    rush = fields.Boolean()
    prior = FormInteger(
        range_error='Priority must be between 1 and 10',
        allow_none=True,
        error_messages={'invalid': 'Not a valid integer value.'},
        validate=validate.Range(min=1, max=10, error='Priority must be between 1 and 10'),
    )
    logtype = fields.String(
        required=True,
        error_messages={'required': 'Log Type is required', 'null': 'Log Type is required'},
        validate=[
            _not_blank('Log Type is required'),
            validate.OneOf(LOG_TYPES, error='Not a valid choice.'),
        ],
    )
    colorf = FormInteger(
        range_error='Number of colors must be a non-negative number',
        allow_none=True,
        error_messages={'invalid': 'Not a valid integer value.'},
        validate=validate.Range(min=0, error='Number of colors must be a non-negative number'),
    )
    ref_artlo = fields.String(
        allow_none=True,
        validate=[
            validate.Length(min=5, max=5, error='Art Reference must be exactly 5 characters'),
            validate.Regexp(r'^[A-Za-z0-9]*$', error='Art Reference must contain only letters and numbers'),
        ],
    )
    howship = FormInteger(
        range_error='How Shipped must be a positive number',
        allow_none=True,
        error_messages={'invalid': 'Not a valid integer value.'},
        validate=validate.Range(min=1, error='How Shipped must be a positive number'),
    )
    artno = fields.String(
        allow_none=True,
        validate=[
            validate.Length(min=4, max=5, error='Artist ID must be between 4 and 5 characters'),
            validate.Regexp(r'^[A-Za-z0-9]*$', error='Artist ID must contain only letters and numbers'),
        ],
    )
    datout = fields.Date(allow_none=True, error_messages={'invalid': 'Not a valid date value.'})

    class Meta:
        unknown = EXCLUDE

    @pre_load
    def normalize_optional_blanks(self, data, **kwargs):
        data = _as_dict(data)
        if not isinstance(data, dict):
            return data
        for name in ('artout', 'dueout', 'print_n', 'artlo', 'prior', 'colorf', 'ref_artlo', 'howship', 'artno', 'datout', 'datin'):
            if _is_blank(data.get(name)):
                data[name] = None
        return data


class UserLoadSchema(Schema):
    username = fields.String(
        required=True,
        error_messages={'required': 'Username is required', 'null': 'Username is required'},
        validate=[
            _not_blank('Username is required'),
            validate.Length(min=3, max=64, error='Username must be between 3 and 64 characters'),
            validate.Regexp(
                r'^[A-Za-z0-9_.\-]+$',
                error='Username can only contain letters, numbers, underscores, periods, and hyphens',
            ),
        ],
    )
    email = fields.String(
        required=True,
        error_messages={'required': 'Email is required', 'null': 'Email is required'},
        validate=[
            _not_blank('Email is required'),
            validate.Length(max=120, error='Email must be less than 120 characters'),
            _validate_email,
        ],
    )
    password = fields.String(
        required=True,
        error_messages={'required': 'This field is required.', 'null': 'This field is required.'},
        validate=[
            _not_blank('This field is required.'),
            validate.Length(min=8, error='Field must be at least 8 characters long.'),
        ],
    )
    role = fields.String(
        load_default='user',
        allow_none=False,
        error_messages={'null': 'Role is required'},
        validate=[
            _not_blank('Role is required'),
            validate.OneOf(('user', 'admin'), error='Role must be one of: user, admin'),
        ],
    )

    class Meta:
        unknown = EXCLUDE


class LoginArgsSchema(Schema):
    username = fields.String(
        required=True,
        error_messages={'required': 'Username is required', 'null': 'Username is required'},
        validate=[
            validate.Length(
                min=3,
                max=64,
                error='Username must be between 3 and 64 characters',
            ),
            validate.Regexp(
                r'^[A-Za-z0-9_.\-]+$',
                error='Username can only contain letters, numbers, underscores, periods, and hyphens',
            ),
        ],
    )
    password = fields.String(
        required=True,
        error_messages={'required': 'Password is required', 'null': 'Password is required'},
        validate=validate.Length(min=8, error='Password must be at least 8 characters'),
    )
    remember = fields.Boolean(load_default=False)

    class Meta:
        unknown = EXCLUDE

    @pre_load
    def reject_blank_credentials(self, data, **kwargs):
        data = _as_dict(data)
        if not isinstance(data, dict):
            return data

        errors = {}
        for field_name, message in (
            ('username', 'Username is required'),
            ('password', 'Password is required'),
        ):
            value = data.get(field_name)
            if value is None or isinstance(value, str) and not value.strip():
                errors[field_name] = [message]
        if errors:
            raise ValidationError(errors)
        return data


class OrderSearchArgsSchema(Schema):
    cust = fields.String(
        allow_none=True,
        validate=[
            _search_length(5, 'Customer ID must be 5 characters or less'),
            _search_alphanumeric,
        ],
    )
    title = fields.String(
        allow_none=True,
        validate=_search_length(100, 'Title must be less than 100 characters'),
    )
    page = fields.Integer(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Integer(load_default=20, validate=validate.Range(min=1))
    sort = fields.String(allow_none=True)

    class Meta:
        unknown = EXCLUDE

    @pre_load
    def normalize_blank_search_terms(self, data, **kwargs):
        data = _as_dict(data)
        if not isinstance(data, dict):
            return data
        for name in ('cust', 'title'):
            if data.get(name) == '':
                data[name] = None
        return data

    @validates_schema
    def validate_search_term(self, data, **kwargs):
        if not data.get('cust') and not data.get('title'):
            raise ValidationError({'cust': ['At least one search field is required']})


class LogArgsSchema(Schema):
    log = fields.String(
        required=True,
        error_messages={'required': 'LOG # is required', 'null': 'LOG # is required'},
        validate=[
            _not_blank('LOG # is required'),
            validate.Length(min=5, max=5, error='LOG # must be exactly 5 characters'),
            validate.Regexp(r'^[A-Za-z0-9]+$', error='LOG # must contain only letters and numbers'),
        ],
    )

    class Meta:
        unknown = EXCLUDE


class DueoutArgsSchema(Schema):
    start_date = fields.Date(
        load_default=None,
        allow_none=True,
        error_messages={'invalid': 'Not a valid date value.'},
    )
    end_date = fields.Date(
        load_default=None,
        allow_none=True,
        error_messages={'invalid': 'Not a valid date value.'},
    )

    class Meta:
        unknown = EXCLUDE

    @pre_load
    def normalize_blank_dates(self, data, **kwargs):
        data = _as_dict(data)
        if not isinstance(data, dict):
            return data
        for name in ('start_date', 'end_date'):
            if _is_blank(data.get(name)):
                data[name] = None
        return data

    @validates_schema
    def validate_date_range(self, data, **kwargs):
        start = data.get('start_date')
        end = data.get('end_date')
        if start is None and end is not None:
            raise ValidationError({'start_date': ['Start date is required']})
        if start is not None and end is None:
            raise ValidationError({'end_date': ['End date is required']})
        if start is not None and end is not None and not is_valid_date_range(start, end):
            raise ValidationError({'end_date': ['End date must be after start date']})
