from flask import request, jsonify
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
bootstrap = Bootstrap5()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page.'

@login.unauthorized_handler
def unauthorized():
    if request.path.startswith('/api'):
        return jsonify({'error': 'Unauthorized', 'message': 'Authentication is required to access this resource'}), 401
    from flask import redirect, url_for, flash
    flash(login.login_message)
    return redirect(url_for(login.login_view))

marshmallow = Marshmallow()
