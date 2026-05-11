from app import login_manager, mongo
from flask_login import UserMixin
from werkzeug.security import check_password_hash
from bson.objectid import ObjectId
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data.get('_id'))
        self.username = user_data.get('username')
        self.password_hash = user_data.get('password_hash')
        self.role = user_data.get('role')
        # Add email support (Ensure your MongoDB documents have an 'email' field)
        self.email = user_data.get('email')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_token(self):
        """Generates a signed token containing the user ID."""
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        """Verifies the token and returns the user data if valid."""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=expires_sec)['user_id']
        except Exception:
            return None
        return mongo.db.users.find_one({'_id': ObjectId(user_id)})

@login_manager.user_loader
def load_user(user_id):
    user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    if user_data:
        return User(user_data)
    return None