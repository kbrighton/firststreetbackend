from flask import Flask
from flask_bootstrap import Bootstrap5

from config import Config
from app.extensions import db, migrate,bootstrap,login


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    from .models import Customer,Order
    # Initialize Flask extensions here
    db.init_app(app)
    migrate.init_app(app,db)

    bootstrap.init_app(app)
    login.init_app(app)


    # Register blueprints here
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')


    @app.route('/test/')
    def test_page():
        return '<h1>Testing the Flask Application Factory Pattern</h1>'

    return app