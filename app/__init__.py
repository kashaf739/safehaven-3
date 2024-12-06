from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_pymongo import PyMongo
from flask_session import Session
import os
import secrets
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
session = Session()
mongo = PyMongo()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(16))
    app.config['SESSION_TYPE'] = 'filesystem'
    
    # MongoDB Configuration - Direct connection configuration
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/safehaven?directConnection=true'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    try:
        # Initialize SQL extensions
        db.init_app(app)
        bcrypt.init_app(app)
        login_manager.init_app(app)
        session.init_app(app)
        
        # Initialize MongoDB
        mongo.init_app(app)
        
        # Test MongoDB connection
        with app.app_context():
            mongo.db.command('ping')
            logger.info("MongoDB connection successful!")
            
            # Try to create patients collection
            try:
                mongo.db.create_collection('patients')
                logger.info("MongoDB 'patients' collection created successfully")
            except Exception as e:
                # Collection might already exist, which is fine
                logger.info(f"Note: {str(e)}")

    except Exception as e:
        logger.error(f"Error during initialization: {str(e)}")
        raise

    # Configure login manager
    login_manager.login_view = 'login'
    login_manager.login_message_category = 'info'

    # Create SQL database tables
    with app.app_context():
        db.create_all()
        logger.info("SQL database tables created successfully")

    # Register routes
    from app.routes import register_routes
    register_routes(app)
    logger.info("Routes registered successfully")

    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))