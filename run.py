# This file's only job is to create and run the app.
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)