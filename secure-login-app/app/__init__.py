from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
import os

db = SQLAlchemy()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object('app.config.Config')

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from .routes import main
    app.register_blueprint(main)

    return app