import os
import json
from dotenv import load_dotenv

load_dotenv()

# --- RECONSTRUCT GOOGLE CREDENTIALS IN PRODUCTION ---
# Since credentials.json and token.json are ignored in Git and Docker for security,
# we recreate them from environment variables (Secrets) when running in production.
if not os.path.exists('credentials.json') and os.environ.get('GOOGLE_CREDENTIALS_JSON'):
    with open('credentials.json', 'w') as f:
        f.write(os.environ.get('GOOGLE_CREDENTIALS_JSON'))

if not os.path.exists('token.json') and os.environ.get('GOOGLE_TOKEN_JSON'):
    with open('token.json', 'w') as f:
        f.write(os.environ.get('GOOGLE_TOKEN_JSON'))

class Config:
    # A secret key is required for session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-super-secret-key-you-should-change'
    
    # --- MONGODB CONFIGURATION ---
    # Loaded from .env to prevent exposing credentials
    MONGO_URI = os.environ.get('MONGO_URI')
    
    # --- MAIL CONFIGURATION ---
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'jagankk9605@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = 'jagankk9605@gmail.com'