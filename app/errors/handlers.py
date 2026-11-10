from flask import jsonify, render_template, request
from flask_wtf.csrf import CSRFError
from marshmallow import ValidationError as MarshmallowValidationError

from app.errors.exceptions import BaseAppException
from app.extensions import db


def api_error(status, error, message, fields=None):
    """Build the standard JSON response used for API errors."""
    payload = {
        'error': error,
        'message': message,
        'status': status,
    }
    if fields is not None:
        payload['fields'] = fields
    return jsonify(payload), status


def _is_api_request():
    return request.path == '/api' or request.path.startswith('/api/')


def _error_message(error, fallback):
    return getattr(error, 'description', None) or fallback


def register_error_handlers(app):
    """Register error handlers with the Flask application."""

    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 Not Found errors."""
        app.logger.warning(f"404 error: {request.url}")
        if _is_api_request():
            return api_error(404, 'Not Found', _error_message(error, 'The requested resource was not found'))
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server Error."""
        app.logger.error(f"500 error: {str(error)}")
        db.session.rollback()
        if _is_api_request():
            return api_error(500, 'Internal Server Error', 'An unexpected error occurred')
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle 403 Forbidden errors."""
        app.logger.warning(f"403 error: {request.url}")
        if _is_api_request():
            return api_error(
                403,
                'Forbidden',
                _error_message(error, 'You do not have permission to access this resource'),
            )
        return render_template('errors/403.html'), 403

    @app.errorhandler(400)
    def bad_request_error(error):
        """Handle 400 Bad Request errors."""
        app.logger.warning(f"400 error: {request.url}")
        if _is_api_request():
            return api_error(400, 'Bad Request', _error_message(error, 'The request could not be understood'))
        return render_template('errors/400.html'), 400

    @app.errorhandler(401)
    def unauthorized_error(error):
        """Handle 401 Unauthorized errors."""
        app.logger.warning(f"401 error: {request.url}")
        if _is_api_request():
            return api_error(
                401,
                'Unauthorized',
                _error_message(error, 'Authentication is required to access this resource'),
            )
        return render_template('errors/401.html'), 401

    @app.errorhandler(405)
    def method_not_allowed_error(error):
        """Handle 405 Method Not Allowed errors."""
        app.logger.warning(f"405 error: {request.method} {request.url}")
        if _is_api_request():
            return api_error(
                405,
                'Method Not Allowed',
                _error_message(error, 'The method is not allowed for the requested URL.'),
            )
        return render_template('errors/405.html'), 405

    @app.errorhandler(BaseAppException)
    def handle_base_app_exception(error):
        """Handle all custom application exceptions."""
        app.logger.error(f"Application error: {str(error)}")

        if _is_api_request():
            fields = (error.payload or {}).get('fields')
            return api_error(error.status_code, error.error, error.message, fields)

        return render_template(f'errors/{error.status_code}.html'), error.status_code

    @app.errorhandler(CSRFError)
    def handle_csrf_error(error):
        """Handle missing or invalid CSRF tokens."""
        app.logger.warning(f"CSRF error: {request.method} {request.url}")
        if _is_api_request():
            return api_error(400, 'CSRF Error', _error_message(error, 'The CSRF token is missing or invalid.'))
        return render_template('errors/400.html'), 400

    @app.errorhandler(MarshmallowValidationError)
    def handle_marshmallow_validation_error(error):
        """Return field-level validation errors for API requests."""
        if _is_api_request():
            return api_error(400, 'Validation Error', 'Input validation failed', error.messages)
        return render_template('errors/400.html'), 400
