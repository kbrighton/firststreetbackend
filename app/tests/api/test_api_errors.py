import pytest
from flask import abort
from marshmallow import ValidationError as MarshmallowValidationError

from app.errors.exceptions import ValidationError


@pytest.fixture
def api_error_routes(app):
    @app.get('/api/errors/bad-request')
    def api_bad_request():
        abort(400, description='Invalid request payload')

    @app.get('/api/errors/unauthorized')
    def api_unauthorized():
        abort(401, description='Authentication required')

    @app.get('/api/errors/forbidden')
    def api_forbidden():
        abort(403, description='Access denied')

    @app.get('/api/errors/not-found')
    def api_not_found():
        abort(404, description='No such API resource')

    @app.get('/api/errors/server-error')
    def api_server_error():
        abort(500, description='Unexpected failure')

    @app.get('/api/errors/custom')
    def api_custom_exception():
        raise ValidationError(
            'Invalid input data provided',
            payload={'fields': {'name': ['Required field']}}
        )

    @app.get('/api/errors/marshmallow')
    def api_marshmallow_exception():
        raise MarshmallowValidationError({'email': ['Not a valid email address.']})

    @app.get('/page/method-not-allowed')
    def page_method_not_allowed():
        return 'GET only'


def assert_api_error(response, status, error, message):
    assert response.status_code == status
    assert response.is_json
    assert response.get_json() == {
        'error': error,
        'message': message,
        'status': status,
    }


def test_api_http_errors_use_common_json_contract(client, api_error_routes):
    cases = (
        ('/api/errors/bad-request', 400, 'Bad Request', 'Invalid request payload'),
        ('/api/errors/unauthorized', 401, 'Unauthorized', 'Authentication required'),
        ('/api/errors/forbidden', 403, 'Forbidden', 'Access denied'),
        ('/api/errors/not-found', 404, 'Not Found', 'No such API resource'),
        ('/api/errors/server-error', 500, 'Internal Server Error', 'An unexpected error occurred'),
    )

    for path, status, error, message in cases:
        assert_api_error(client.get(path), status, error, message)

    method_error = client.post('/api/errors/bad-request')
    assert method_error.status_code == 405
    assert method_error.is_json
    assert method_error.get_json() == {
        'error': 'Method Not Allowed',
        'message': 'The method is not allowed for the requested URL.',
        'status': 405,
    }


def test_api_custom_exception_uses_common_json_contract(client, api_error_routes):
    response = client.get('/api/errors/custom')

    assert response.status_code == 400
    assert response.is_json
    assert response.get_json() == {
        'error': 'Validation Error',
        'message': 'Invalid input data provided',
        'status': 400,
        'fields': {'name': ['Required field']},
    }


def test_api_marshmallow_validation_error_includes_field_errors(client, api_error_routes):
    response = client.get('/api/errors/marshmallow')

    assert response.status_code == 400
    assert response.is_json
    assert response.get_json() == {
        'error': 'Validation Error',
        'message': 'Input validation failed',
        'status': 400,
        'fields': {'email': ['Not a valid email address.']},
    }


def test_non_api_not_found_and_method_not_allowed_remain_html(client, api_error_routes):
    not_found = client.get('/page/missing')
    method_not_allowed = client.post('/page/method-not-allowed')

    assert not_found.status_code == 404
    assert not_found.mimetype == 'text/html'
    assert method_not_allowed.status_code == 405
    assert method_not_allowed.mimetype == 'text/html'


def test_api_login_bad_request_uses_common_json_contract(client):
    response = client.post('/api/auth/login', json={})

    assert_api_error(response, 400, 'Bad Request', 'Username and password required')
