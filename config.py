import os

class Config:
    # A secret key is required for session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-super-secret-key-you-should-change'
    
    # --- YOUR UPDATED MONGODB CONFIGURATION ---
    # This now uses the specific connection details for your Cluster0.
    MONGO_URI = os.environ.get('MONGO_URI') or \
        'mongodb+srv://jagankk:Jagankkstm23@cluster0.kqm7txf.mongodb.net/arProjectDB?retryWrites=true&w=majority&appName=Cluster0'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'jagankk9605@gmail.com'
    MAIL_PASSWORD = 'tpld jvoj sbjy axtv' # Use an App Password
    MAIL_DEFAULT_SENDER = 'jagankk9605@gmail.com'