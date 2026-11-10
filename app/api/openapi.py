"""
OpenAPI description of the /api blueprint.

The spec is generated from the registered routes, their docstrings and the
Marshmallow schemas, and is served at GET /api/openapi.json.
"""

import inspect
import re

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flask import current_app, jsonify

from app.api import bp
from app.schemas import CustomerSchema, OrderDetailSchema, OrderSchema, UserSchema
from app.schemas.validation_schemas import LoginArgsSchema, OrderLoadSchema, UserLoadSchema

API_PREFIX = '/api'
WRITE_METHODS = ('post', 'put', 'delete')
CONVERTER_TYPES = {'int': 'integer', 'float': 'number'}

ERROR_SCHEMA = {
    'type': 'object',
    'required': ['error', 'message', 'status'],
    'properties': {
        'error': {'type': 'string'},
        'message': {'type': 'string'},
        'status': {'type': 'integer'},
        'fields': {
            'type': 'object',
            'additionalProperties': {'type': 'array', 'items': {'type': 'string'}},
        },
    },
}
ORDER_LIST_SCHEMA = {
    'type': 'object',
    'required': ['data', 'total', 'page', 'per_page', 'pages'],
    'properties': {
        'data': {'type': 'array', 'items': {'$ref': '#/components/schemas/Order'}},
        'total': {'type': 'integer'},
        'page': {'type': 'integer'},
        'per_page': {'type': 'integer'},
        'pages': {'type': 'integer'},
    },
}
CURRENT_USER_SCHEMA = {
    'type': 'object',
    'required': ['user'],
    'properties': {
        'user': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'username': {'type': 'string'},
                'email': {'type': 'string'},
                'role': {'type': 'string', 'enum': ['user', 'admin']},
                'created_at': {'type': 'string', 'format': 'date-time', 'nullable': True},
            },
        },
    },
}
CSRF_TOKEN_SCHEMA = {
    'type': 'object',
    'required': ['csrf_token'],
    'properties': {'csrf_token': {'type': 'string'}},
}
QUERY_PARAMETERS = {
    'api.get_dueouts': [
        {
            'name': 'start_date',
            'in': 'query',
            'required': False,
            'schema': {'type': 'string', 'format': 'date'},
        },
        {
            'name': 'end_date',
            'in': 'query',
            'required': False,
            'schema': {'type': 'string', 'format': 'date'},
        },
    ],
}

# Request and success-response bodies per (endpoint, method)
REQUEST_BODIES = {
    ('api.create_order', 'post'): 'OrderInput',
    ('api.update_order_by_id', 'put'): 'OrderInput',
    ('api.create_user', 'post'): 'UserInput',
    ('api.update_user', 'put'): 'UserInput',
    ('api.api_login', 'post'): 'LoginRequest',
}
RESPONSE_BODIES = {
    'api.get_orders': ('OrderList', False),
    'api.get_order': ('OrderDetail', False),
    'api.get_order_by_log': ('OrderDetail', False),
    'api.create_order': ('Order', False),
    'api.update_order_by_id': ('Order', False),
    'api.get_dueouts': ('Order', True),
    'api.get_customers': ('Customer', True),
    'api.get_customer': ('Customer', False),
    'api.search_customers': ('Customer', True),
    'api.get_users': ('User', True),
    'api.get_user': ('User', False),
    'api.create_user': ('User', False),
    'api.update_user': ('User', False),
    'api.api_current_user': ('CurrentUser', False),
    'api.api_csrf_token': ('CsrfToken', False),
}
CREATED_ENDPOINTS = {'api.create_order', 'api.create_user', 'api.create_customer'}
NO_CONTENT_ENDPOINTS = {'api.delete_order', 'api.delete_user', 'api.delete_customer'}
PUBLIC_ENDPOINTS = {'api.api_login', 'api.api_csrf_token', 'api.openapi_spec'}


def _ref(name, many=False):
    schema = {'$ref': f'#/components/schemas/{name}'}
    return {'type': 'array', 'items': schema} if many else schema


def _error_response(description):
    return {'description': description, 'content': {'application/json': {'schema': _ref('Error')}}}


def _summary(view):
    doc = inspect.getdoc(view) or ''
    return doc.split('---')[0].strip().splitlines()[0] if doc.strip() else view.__name__


def _path_parameters(rule):
    parameters = []
    for converter, name in re.findall(r'<(?:([^:<>]+):)?([^<>]+)>', rule.rule):
        parameters.append({
            'name': name,
            'in': 'path',
            'required': True,
            'schema': {'type': CONVERTER_TYPES.get(converter, 'string')},
        })
    return parameters


def _operation(rule, method, view):
    endpoint = rule.endpoint
    operation = {
        'summary': _summary(view),
        'description': inspect.getdoc(view) or '',
        'tags': [rule.rule[len(API_PREFIX):].strip('/').split('/')[0] or 'api'],
        'operationId': f'{endpoint.split(".")[-1]}_{method}',
        'responses': {
            '400': _error_response('Bad request, validation error or CSRF error'),
            '500': _error_response('Internal server error'),
        },
    }

    parameters = _path_parameters(rule)
    parameters.extend(QUERY_PARAMETERS.get(endpoint, []))
    if parameters:
        operation['parameters'] = parameters
        operation['responses']['404'] = _error_response('Not found')

    if (endpoint, method) in REQUEST_BODIES:
        operation['requestBody'] = {
            'required': True,
            'content': {'application/json': {'schema': _ref(REQUEST_BODIES[(endpoint, method)])}},
        }

    if endpoint in NO_CONTENT_ENDPOINTS:
        operation['responses']['204'] = {'description': 'No content'}
    else:
        status = '201' if endpoint in CREATED_ENDPOINTS else '200'
        success = {'description': 'Success'}
        if endpoint in RESPONSE_BODIES:
            name, many = RESPONSE_BODIES[endpoint]
            success['content'] = {'application/json': {'schema': _ref(name, many)}}
        operation['responses'][status] = success

    if endpoint not in PUBLIC_ENDPOINTS:
        operation['responses']['401'] = _error_response('Authentication required')
        operation['responses']['403'] = _error_response('Forbidden')

    security = {}
    if endpoint not in PUBLIC_ENDPOINTS:
        security['sessionCookie'] = []
    if method in WRITE_METHODS:
        security['csrfToken'] = []
    operation['security'] = [security] if security else []
    return operation


def build_spec(app):
    """Build the OpenAPI spec for every /api route registered on the app."""
    spec = APISpec(
        title='First Street API',
        version='1.0.0',
        openapi_version='3.0.3',
        plugins=[FlaskPlugin(), MarshmallowPlugin()],
        info={
            'description': (
                'Session-cookie authenticated API. Fetch a token from GET /api/auth/csrf '
                'and send it in the X-CSRFToken header on POST, PUT and DELETE requests.'
            ),
        },
    )
    spec.components.security_scheme(
        'sessionCookie', {'type': 'apiKey', 'in': 'cookie', 'name': app.config.get('SESSION_COOKIE_NAME', 'session')}
    )
    spec.components.security_scheme('csrfToken', {'type': 'apiKey', 'in': 'header', 'name': 'X-CSRFToken'})

    spec.components.schema('Order', schema=OrderSchema)
    spec.components.schema('OrderDetail', schema=OrderDetailSchema)
    spec.components.schema('Customer', schema=CustomerSchema)
    spec.components.schema('User', schema=UserSchema)
    spec.components.schema('OrderInput', schema=OrderLoadSchema)
    spec.components.schema('UserInput', schema=UserLoadSchema)
    spec.components.schema('Error', ERROR_SCHEMA)
    spec.components.schema('OrderList', ORDER_LIST_SCHEMA)
    spec.components.schema('CurrentUser', CURRENT_USER_SCHEMA)
    spec.components.schema('CsrfToken', CSRF_TOKEN_SCHEMA)
    spec.components.schema('LoginRequest', schema=LoginArgsSchema)

    for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
        if not rule.rule.startswith(API_PREFIX + '/'):
            continue
        view = app.view_functions[rule.endpoint]
        methods = sorted(m.lower() for m in rule.methods if m not in ('HEAD', 'OPTIONS'))
        operations = {method: _operation(rule, method, view) for method in methods}
        spec.path(view=view, app=app, operations=operations)

    return spec


@bp.route('/openapi.json')
def openapi_spec():
    """Get the OpenAPI description of the API."""
    return jsonify(build_spec(current_app).to_dict())
