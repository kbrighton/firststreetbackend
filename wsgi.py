import os
from app import create_app

# Get the environment from FLASK_ENV, defaulting to 'development'
config_name = os.environ.get('FLASK_ENV', 'development')

# Create the application instance
application = create_app(config_name)

# Add a simple health check route
@application.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    return {'status': 'healthy'}, 200

if __name__ == '__main__':
    # Run the application with debug mode based on environment
    debug = os.environ.get('FLASK_DEBUG', application.config.get('DEBUG', False))
    application.run(debug=debug)
