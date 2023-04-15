from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
bootstrap = Bootstrap5()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page.'
