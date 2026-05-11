from app import create_app, mongo
from werkzeug.security import generate_password_hash

# Create an app instance to work with
app = create_app()

@app.cli.command("init-db")
def init_db():
    """Initializes the database and creates the default admin."""
    with app.app_context():
        users_collection = mongo.db.users
        
        # Check if the admin user already exists
        if users_collection.find_one({'username': 'admin123'}):
            print("Admin user already exists.")
            return

        # Hash the password for security
        hashed_password = generate_password_hash('admin123')
        
        # Insert the admin user document
        users_collection.insert_one({
            'username': 'admin123',
            'password_hash': hashed_password,
            'role': 'admin'
        })
        print("Default admin user 'admin123' created successfully.")