# app.py
from flask import Flask
from flask_cors import CORS
from api import api
from views import main
import os
from database_manager import DatabaseManager
from emailer.EmailSender import EmailSender
from flask_login import LoginManager
from bson.objectid import ObjectId
from auth.models import User
from auth.routes import auth_bp

def create_app():
    email_sender = EmailSender()

    # Create the Flask application
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db_manager = DatabaseManager()
    mongo = db_manager.get_db()

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = (
        "auth.login"  # Redirect to login view if not authenticated
    )

    # User Loader function
    @login_manager.user_loader
    def load_user(user_id):
        """
        Load a user from the database by user_id.
        """
        user_doc = mongo.users.find_one({"_id": ObjectId(user_id)})
        if user_doc:
            return User.from_db(user_doc)
        return None


    # Register blueprints
    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(main)
    app.register_blueprint(auth_bp)

    # Enable CORS for the entire app
    CORS(app, origins="*")
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)  # Enable debug mode for development purposes
