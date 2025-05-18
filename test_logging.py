import os
import sys
from flask import Flask
from app import create_app
from app.logging import get_logger

# Create a logger for this script
logger = get_logger(__name__)

def test_logging():
    """Test the logging functionality."""
    # Log messages at different levels
    logger.debug("This is a DEBUG message from test_logging.py")
    logger.info("This is an INFO message from test_logging.py")
    logger.warning("This is a WARNING message from test_logging.py")
    logger.error("This is an ERROR message from test_logging.py")
    logger.critical("This is a CRITICAL message from test_logging.py")
    
    # Create the app to test app-specific logging
    app = create_app('development')
    
    # Use the app context to test app-specific logging
    with app.app_context():
        app.logger.debug("This is a DEBUG message from the app logger")
        app.logger.info("This is an INFO message from the app logger")
        app.logger.warning("This is a WARNING message from the app logger")
        app.logger.error("This is an ERROR message from the app logger")
        app.logger.critical("This is a CRITICAL message from the app logger")
    
    print("Logging test completed. Check the logs to verify.")

if __name__ == "__main__":
    # Set the log level to DEBUG for testing
    os.environ['LOG_LEVEL'] = 'DEBUG'
    
    # Run the test
    test_logging()