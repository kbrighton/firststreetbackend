import unittest
from app import create_app
from flask import url_for, jsonify
from app.errors.exceptions import ResourceNotFoundError, ValidationError, AuthorizationError

class TestErrorHandlers(unittest.TestCase):
    """Test the custom error handlers."""

    def setUp(self):
        """Set up the test environment."""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()

    def test_404_error(self):
        """Test the 404 error handler."""
        response = self.client.get('/nonexistent-page')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'404 Not Found', response.data)
        self.assertIn(b'Sorry, the page you requested could not be found', response.data)

    def test_500_error(self):
        """Test the 500 error handler."""
        # Create a route that raises an exception
        @self.app.route('/trigger-error')
        def trigger_error():
            raise Exception('Test exception')

        response = self.client.get('/trigger-error')
        self.assertEqual(response.status_code, 500)
        self.assertIn(b'500 Internal Server Error', response.data)
        self.assertIn(b'Sorry, something went wrong on our end', response.data)

    def test_403_error(self):
        """Test the 403 error handler."""
        # Create a route that returns a 403 error
        @self.app.route('/forbidden')
        def forbidden():
            return self.app.response_class(status=403)

        response = self.client.get('/forbidden')
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'403 Forbidden', response.data)
        self.assertIn(b'Sorry, you don\'t have permission to access this page', response.data)

    def test_400_error(self):
        """Test the 400 error handler."""
        # Create a route that returns a 400 error
        @self.app.route('/bad-request')
        def bad_request():
            return self.app.response_class(status=400)

        response = self.client.get('/bad-request')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'400 Bad Request', response.data)
        self.assertIn(b'Sorry, your request contains invalid parameters or syntax', response.data)

    def test_405_error(self):
        """Test the 405 error handler."""
        # Create a route that only accepts GET requests
        @self.app.route('/method-not-allowed', methods=['GET'])
        def method_not_allowed():
            return "This route only accepts GET requests"

        # Send a POST request to trigger a 405 error
        response = self.client.post('/method-not-allowed')
        self.assertEqual(response.status_code, 405)
        self.assertIn(b'405 Method Not Allowed', response.data)
        self.assertIn(b'Sorry, the method used is not allowed for this resource', response.data)

    def test_resource_not_found_error(self):
        """Test the ResourceNotFoundError handler."""
        # Create a route that raises a ResourceNotFoundError
        @self.app.route('/resource-not-found')
        def resource_not_found():
            raise ResourceNotFoundError("The requested item was not found")

        response = self.client.get('/resource-not-found')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'404 Not Found', response.data)

    def test_validation_error(self):
        """Test the ValidationError handler."""
        # Create a route that raises a ValidationError
        @self.app.route('/validation-error')
        def validation_error():
            raise ValidationError("Invalid input data provided")

        response = self.client.get('/validation-error')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'400 Bad Request', response.data)

    def test_authorization_error(self):
        """Test the AuthorizationError handler."""
        # Create a route that raises an AuthorizationError
        @self.app.route('/authorization-error')
        def authorization_error():
            raise AuthorizationError("You don't have permission to access this resource")

        response = self.client.get('/authorization-error')
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'403 Forbidden', response.data)

    def test_api_custom_exception(self):
        """Test custom exceptions in API routes."""
        # Create an API route that raises a ValidationError
        @self.app.route('/api/validation-error')
        def api_validation_error():
            raise ValidationError("Invalid input data provided")

        response = self.client.get('/api/validation-error')
        self.assertEqual(response.status_code, 400)
        # API routes should return JSON
        self.assertEqual(response.content_type, 'application/json')
        # Check the JSON response
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 400)
        self.assertEqual(json_data['message'], "Invalid input data provided")

if __name__ == '__main__':
    unittest.main()
