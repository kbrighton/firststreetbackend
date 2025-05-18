from flask import render_template, current_app, request, jsonify
from app.errors import bp
from app.extensions import db
from app.errors.exceptions import BaseAppException
import logging


def register_error_handlers(app):
    """Register error handlers with the Flask application."""

    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 Not Found errors."""
        app.logger.warning(f"404 error: {request.url}")
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server Error."""
        app.logger.error(f"500 error: {str(error)}")
        db.session.rollback()  # Roll back any failed database sessions
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle 403 Forbidden errors."""
        app.logger.warning(f"403 error: {request.url}")
        return render_template('errors/403.html'), 403

    @app.errorhandler(400)
    def bad_request_error(error):
        """Handle 400 Bad Request errors."""
        app.logger.warning(f"400 error: {request.url}")
        return render_template('errors/400.html'), 400

    @app.errorhandler(405)
    def method_not_allowed_error(error):
        """Handle 405 Method Not Allowed errors."""
        app.logger.warning(f"405 error: {request.method} {request.url}")
        return render_template('errors/405.html'), 405

    @app.errorhandler(BaseAppException)
    def handle_base_app_exception(error):
        """Handle all custom application exceptions."""
        app.logger.error(f"Application error: {str(error)}")

        # For API requests, return JSON response
        if request.path.startswith('/api'):
            response = jsonify(error.to_dict())
            response.status_code = error.status_code
            return response

        # For web requests, render appropriate template
        return render_template(f'errors/{error.status_code}.html'), error.status_code


# Register error handlers with blueprint for backward compatibility
@bp.app_errorhandler(404)
def not_found_error_bp(error):
    """Handle 404 Not Found errors."""
    current_app.logger.warning(f"404 error (blueprint): {request.url}")
    return render_template('errors/404.html'), 404


@bp.app_errorhandler(500)
def internal_error_bp(error):
    """Handle 500 Internal Server Error."""
    current_app.logger.error(f"500 error (blueprint): {str(error)}")
    db.session.rollback()  # Roll back any failed database sessions
    return render_template('errors/500.html'), 500


@bp.app_errorhandler(403)
def forbidden_error_bp(error):
    """Handle 403 Forbidden errors."""
    current_app.logger.warning(f"403 error (blueprint): {request.url}")
    return render_template('errors/403.html'), 403


@bp.app_errorhandler(400)
def bad_request_error_bp(error):
    """Handle 400 Bad Request errors."""
    current_app.logger.warning(f"400 error (blueprint): {request.url}")
    return render_template('errors/400.html'), 400


@bp.app_errorhandler(405)
def method_not_allowed_error_bp(error):
    """Handle 405 Method Not Allowed errors."""
    current_app.logger.warning(f"405 error (blueprint): {request.method} {request.url}")
    return render_template('errors/405.html'), 405


@bp.app_errorhandler(BaseAppException)
def handle_base_app_exception_bp(error):
    """Handle all custom application exceptions (blueprint version)."""
    current_app.logger.error(f"Application error (blueprint): {str(error)}")

    # For API requests, return JSON response
    if request.path.startswith('/api'):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    # For web requests, render appropriate template
    return render_template(f'errors/{error.status_code}.html'), error.status_code
