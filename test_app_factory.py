import os
import unittest
import logging
from app import create_app
from flask import current_app


class TestAppFactory(unittest.TestCase):
    """Test suite for the application factory pattern."""

    def setUp(self):
        """Set up test environment."""
        # Save original environment variable
        self.original_env = os.environ.get('FLASK_ENV')

        # Set up a test logger to capture log messages
        self.log_capture = []
        self.log_handler = TestLogHandler(self.log_capture)
        logging.getLogger().addHandler(self.log_handler)
        logging.getLogger().setLevel(logging.INFO)

    def tearDown(self):
        """Clean up after tests."""
        # Restore original environment variable
        if self.original_env:
            os.environ['FLASK_ENV'] = self.original_env
        elif 'FLASK_ENV' in os.environ:
            del os.environ['FLASK_ENV']

        # Remove the test log handler
        logging.getLogger().removeHandler(self.log_handler)

    def test_development_config(self):
        """Test that the development configuration works correctly."""
        os.environ['FLASK_ENV'] = 'development'
        app = create_app()

        with app.app_context():
            self.assertTrue(app.config['DEBUG'])
            self.assertTrue(app.config['DEVELOPMENT'])
            self.assertFalse(app.config['TESTING'])
            self.assertEqual(current_app, app)

            # Check that database URI is properly configured
            self.assertIsNotNone(app.config['SQLALCHEMY_DATABASE_URI'])

        print("Development configuration test passed!")

    def test_production_config(self):
        """Test that the production configuration works correctly."""
        os.environ['FLASK_ENV'] = 'production'
        app = create_app()

        with app.app_context():
            self.assertFalse(app.config['DEBUG'])
            # In production, DEVELOPMENT should not be True
            self.assertFalse(app.config.get('DEVELOPMENT', False))
            self.assertFalse(app.config['TESTING'])
            self.assertEqual(current_app, app)

            # Test production-specific settings
            self.assertTrue(app.config['SESSION_COOKIE_SECURE'])
            self.assertTrue(app.config['REMEMBER_COOKIE_SECURE'])
            self.assertTrue(app.config['WTF_CSRF_ENABLED'])

        print("Production configuration test passed!")

    def test_testing_config(self):
        """Test that the testing configuration works correctly."""
        os.environ['FLASK_ENV'] = 'testing'
        app = create_app()

        with app.app_context():
            self.assertTrue(app.config['TESTING'])
            self.assertFalse(app.config['WTF_CSRF_ENABLED'])
            self.assertEqual(current_app, app)

            # Check that database URI is properly configured for testing
            self.assertIn('test.db', app.config['SQLALCHEMY_DATABASE_URI'])

        print("Testing configuration test passed!")

    def test_staging_config(self):
        """Test that the staging configuration works correctly."""
        os.environ['FLASK_ENV'] = 'staging'
        app = create_app()

        with app.app_context():
            self.assertTrue(app.config['DEBUG'])
            self.assertTrue(app.config['DEVELOPMENT'])
            self.assertFalse(app.config['TESTING'])
            self.assertEqual(current_app, app)

            # Check that database URI is properly configured
            self.assertIsNotNone(app.config['SQLALCHEMY_DATABASE_URI'])

        print("Staging configuration test passed!")

    def test_invalid_config(self):
        """Test that an invalid configuration raises an error."""
        os.environ['FLASK_ENV'] = 'invalid_config'

        with self.assertRaises(ValueError):
            create_app()

        print("Invalid configuration test passed!")


class TestLogHandler(logging.Handler):
    """Custom log handler that captures log records for testing."""

    def __init__(self, log_list):
        """Initialize with a list to store log records."""
        super().__init__()
        self.log_list = log_list

    def emit(self, record):
        """Store the log record in the list."""
        self.log_list.append(record)


if __name__ == '__main__':
    print("Testing application factory with different configurations...")
    unittest.main(verbosity=2)
    print("All tests passed!")
