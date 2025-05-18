import os
from flask import Flask

from app.extensions import db, migrate, bootstrap, login, marshmallow
from app.logging import init_logging
from config import config


def create_app(config_name=None):
    """
    Application factory function that creates and configures the Flask application.

    Args:
        config_name (str, optional): The name of the configuration to use.
            If not provided, it will be read from the FLASK_ENV environment variable,
            defaulting to 'development' if not set.

    Returns:
        Flask: The configured Flask application instance.
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    # Ensure we have a valid configuration
    if config_name not in config:
        raise ValueError(f"Invalid configuration: {config_name}. "
                         f"Available configurations: {', '.join(config.keys())}")

    app = Flask(__name__)

    # Load default configuration
    app.config.from_object(config['default'])

    # Load environment specific configuration
    app.config.from_object(config[config_name])

    # Load optional configuration from instance folder
    app.config.from_pyfile('config.py', silent=True)

    # Load configuration from environment variables prefixed with FLASK_
    app.config.from_envvar('FLASK_CONFIG', silent=True)

    # Initialize environment-specific settings
    config[config_name].init_app(app)

    # Initialize extensions
    _init_extensions(app)

    # Register blueprints
    _register_blueprints(app)

    # Register error handlers
    _register_error_handlers(app)

    # Initialize logging
    init_logging(app)

    return app


def _init_extensions(app):
    """Initialize Flask extensions."""
    # Import models to ensure they're registered with SQLAlchemy
    from app.models import Customer, Order, User

    db.init_app(app)
    migrate.init_app(app, db)
    marshmallow.init_app(app)
    bootstrap.init_app(app)
    login.init_app(app)


def _register_blueprints(app):
    """Register Flask blueprints."""
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)


def _register_error_handlers(app):
    """Register error handlers."""
    from app.errors.handlers import register_error_handlers
    register_error_handlers(app)
