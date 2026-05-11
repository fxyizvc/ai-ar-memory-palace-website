from flask import Flask
from config import Config
from flask_pymongo import PyMongo
from flask_login import LoginManager
from flask_mail import Mail

# Initialize extensions
# We name it 'mongo' so we can call it from anywhere as 'mongo.db...'
mongo = PyMongo()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
mail = Mail() # Add this

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with the app
    mongo.init_app(app)
    login_manager.init_app(app)

    mail.init_app(app) # Initialize it here

    # Import and register blueprints
    from .auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from .admin.routes import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Import models here to avoid circular imports
    from . import models

    return app