import os
import logging
from logging.handlers import RotatingFileHandler, SMTPHandler
import sys

def init_logging(app):
    """
    Initialize logging for the application.

    This sets up logging handlers and formatters based on the application configuration.
    It configures both file and console logging with appropriate log levels.

    Args:
        app: The Flask application instance
    """
    # Get log level from config
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s [%(name)s] %(message)s [in %(pathname)s:%(lineno)d]'
    )

    # Clear existing handlers to avoid duplicates when reloading in debug mode
    if root_logger.handlers:
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

    # Configure console logging
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    root_logger.addHandler(console_handler)

    # Configure file logging if not in debug or testing mode
    if not app.debug and not app.testing:
        # Log to stdout if configured
        if app.config.get('LOG_TO_STDOUT'):
            # Already configured console handler above
            pass
        else:
            # Ensure logs directory exists
            if not os.path.exists('logs'):
                os.mkdir('logs')

            # Configure rotating file handler
            file_handler = RotatingFileHandler(
                'logs/firststreet.log',
                maxBytes=10240,
                backupCount=10
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(log_level)
            root_logger.addHandler(file_handler)

        # Configure email logging for errors in production
        if app.config.get('MAIL_SERVER') and app.config.get('ADMINS'):
            auth = None
            if app.config.get('MAIL_USERNAME') or app.config.get('MAIL_PASSWORD'):
                auth = (app.config.get('MAIL_USERNAME'), app.config.get('MAIL_PASSWORD'))

            secure = None
            if app.config.get('MAIL_USE_TLS'):
                secure = ()

            mail_handler = SMTPHandler(
                mailhost=(app.config.get('MAIL_SERVER'), app.config.get('MAIL_PORT')),
                fromaddr=f'no-reply@{app.config.get("MAIL_SERVER")}',
                toaddrs=app.config.get('ADMINS'),
                subject='FirstStreet Application Error',
                credentials=auth,
                secure=secure
            )
            mail_handler.setLevel(logging.ERROR)
            mail_handler.setFormatter(formatter)
            root_logger.addHandler(mail_handler)

    # Log application startup
    env = os.environ.get('FLASK_ENV', 'development')
    app.logger.info(f'FirstStreet startup in {env} mode')

    return root_logger

def get_logger(name):
    """
    Get a logger for a specific module.

    Args:
        name: The name of the module (typically __name__)

    Returns:
        A configured logger instance
    """
    return logging.getLogger(name)
