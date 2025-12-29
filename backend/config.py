"""
Configuration module for the e-learning application.
Handles environment variables and application settings.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration class."""
    
    MONGODB_URI = os.getenv(
        'MONGODB_URI', 
        'mongodb+srv://cursorrp_db_user:ka1r5cs2fPu1fcIk@cluster0.7fr4den.mongodb.net/elearning?retryWrites=true&w=majority&appName=Cluster0'
    )
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'elearning-jwt-secret-key-2024-secure')
    JWT_EXPIRATION_HOURS = 24
    

class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    

class ProductionConfig(Config):
    """Production configuration."""
    
    DEBUG = False


def get_config():
    """Return the appropriate configuration based on environment."""
    env = os.getenv('FLASK_ENV', 'development')
    
    if env == 'production':
        return ProductionConfig()
    return DevelopmentConfig()


