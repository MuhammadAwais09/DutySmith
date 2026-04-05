# config.py
# Application Configuration

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'duty-smith-secret-key-change-in-production')
    
    # Firebase
    FIREBASE_API_KEY = os.environ.get('FIREBASE_API_KEY', 'AIzaSyDdRS9eN2K6Hq39RS6eoYnyUWqkjseQwzY')
    FIREBASE_DATABASE_URL = os.environ.get('FIREBASE_DATABASE_URL', 'https://dutysmith-25ccb-default-rtdb.firebaseio.com')
    FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID', 'dutysmith-25ccb')
    
    # Session
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    
    # App
    APP_NAME = os.environ.get('APP_NAME', 'Duty Smith')
    APP_VERSION = os.environ.get('APP_VERSION', '2.0.0')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True


# Config dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}