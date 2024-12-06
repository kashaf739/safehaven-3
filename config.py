# config.py

import os

class Config:
    """Base configuration class"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'mysecretkey')  # Default secret key
    SESSION_TYPE = 'filesystem'
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable modification tracking
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/safehaven')  # Default MongoDB URI

class DevelopmentConfig(Config):
    """Development configuration"""
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'
    DEBUG = True

class TestingConfig(Config):
    """Testing configuration"""
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    TESTING = True

class ProductionConfig(Config):
    """Production configuration"""
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///prod.db')
    DEBUG = False
