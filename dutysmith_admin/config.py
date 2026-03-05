import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'duty-smith-secret-key-change-in-production'
    FIREBASE_CREDENTIALS = os.environ.get('FIREBASE_CREDENTIALS') or 'firebase-credentials.json'
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour