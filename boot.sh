#!/bin/sh
source venv/bin/activate

# Set default environment to production if not specified
export FLASK_ENV=${FLASK_ENV:-production}

exec gunicorn --bind 0.0.0.0:5000 wsgi:application
