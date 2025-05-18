"""
Main blueprint package for the application's primary functionality.

This package contains the main routes, forms, and views for the application.
It defines a Flask Blueprint that handles the core functionality of the application,
including order management, customer interactions, and search capabilities.
"""

from flask import Blueprint

bp = Blueprint('main', __name__)

from app.main import routes
