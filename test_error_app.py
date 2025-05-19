from flask import Flask, abort, jsonify
from app.errors.handlers import register_error_handlers
from app.errors.exceptions import ResourceNotFoundError, ValidationError, AuthorizationError, DatabaseError
import os

def create_test_app():
    """Create a test Flask application with error handlers."""
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(__file__), 'app', 'templates'))

    # Register error handlers
    register_error_handlers(app)

    # Create test routes that trigger different errors
    @app.route('/')
    def index():
        return "Test App Home"

    @app.route('/404')
    def not_found():
        # Manually trigger a 404 error
        abort(404)

    @app.route('/500')
    def server_error():
        # Manually trigger a 500 error
        raise Exception("Test 500 error")

    @app.route('/403')
    def forbidden():
        # Manually trigger a 403 error
        abort(403)

    @app.route('/400')
    def bad_request():
        # Manually trigger a 400 error
        abort(400)

    @app.route('/405', methods=['GET'])
    def method_not_allowed():
        # This route only accepts GET requests
        # To test the 405 handler, send a POST request to this endpoint
        return "This route only accepts GET requests"

    @app.route('/custom/resource-not-found')
    def resource_not_found():
        # Raise a ResourceNotFoundError
        raise ResourceNotFoundError("The requested item was not found")

    @app.route('/custom/validation-error')
    def validation_error():
        # Raise a ValidationError
        raise ValidationError("Invalid input data provided")

    @app.route('/custom/authorization-error')
    def authorization_error():
        # Raise an AuthorizationError
        raise AuthorizationError("You don't have permission to access this resource")

    @app.route('/custom/database-error')
    def database_error():
        # Raise a DatabaseError
        raise DatabaseError("A database error occurred")

    # API routes that return JSON responses
    @app.route('/api/resource-not-found')
    def api_resource_not_found():
        # Raise a ResourceNotFoundError in an API route
        raise ResourceNotFoundError("API: The requested item was not found")

    @app.route('/api/validation-error')
    def api_validation_error():
        # Raise a ValidationError in an API route
        raise ValidationError("API: Invalid input data provided")

    return app

if __name__ == '__main__':
    app = create_test_app()
    app.config['TESTING'] = True
    app.config['DEBUG'] = True
    app.run(port=5001)
