import os
import logging
from logging.handlers import RotatingFileHandler

basedir = os.path.abspath(os.path.dirname(__file__))
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config(object):
    """Base configuration class with common settings."""
    # Flask settings
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-please-change-in-production')
    SSL_REDIRECT = False

    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        f'sqlite:///{os.path.join(basedir, "app.db")}'
    )

    # UI settings
    BOOTSTRAP_BOOTSWATCH_THEME = 'lumen'
    WTF_CSRF_CHECK_DEFAULT = True

    # Logging settings
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT', False)
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

    @staticmethod
    def init_app(app):
        """Initialize application with configuration settings."""
        # Logging is now configured in app.logging module
        pass


class ProductionConfig(Config):
    """Production environment configuration."""
    # Override database URI to ensure it's set from environment
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    # Production-specific settings
    DEBUG = False
    DEVELOPMENT = False  # Explicitly set to False for production
    WTF_CSRF_ENABLED = True

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # Production-specific initialization
        # Secure cookies
        app.config['SESSION_COOKIE_SECURE'] = True
        app.config['REMEMBER_COOKIE_SECURE'] = True

        # Set strict transport security
        @app.after_request
        def add_security_headers(response):
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            return response


class StagingConfig(Config):
    """Staging environment configuration."""
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'STAGING_DATABASE_URL', 
        os.environ.get('DATABASE_URL', Config.SQLALCHEMY_DATABASE_URI)
    )

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # Staging-specific initialization
        pass


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DEV_DATABASE_URL', 
        os.environ.get('DATABASE_URL', Config.SQLALCHEMY_DATABASE_URI)
    )

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # Development-specific initialization
        pass


class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'TEST_DATABASE_URL', 
        f'sqlite:///{os.path.join(basedir, "test.db")}'
    )
    WTF_CSRF_ENABLED = False

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # Testing-specific initialization
        pass


class DockerConfig(ProductionConfig):
    """Docker environment configuration."""
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # Docker-specific initialization
        # Set LOG_TO_STDOUT to True for Docker environments
        app.config['LOG_TO_STDOUT'] = True


# Configuration dictionary mapping environment names to config classes
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'staging': StagingConfig,
    'docker': DockerConfig,

    'default': DevelopmentConfig
}
