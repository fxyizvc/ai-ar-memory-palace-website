from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from app import mongo, mail # Ensure mail is imported from app
from app.models import User
from flask_mail import Message
from werkzeug.security import generate_password_hash

auth_bp = Blueprint('auth', __name__, template_folder='../templates/auth')

def send_reset_email(user_obj):
    token = user_obj.get_reset_token()
    msg = Message('Password Reset Request',
                  recipients=[user_obj.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('auth.reset_token', token=token, _external=True)}

If you did not make this request, simply ignore this email.
'''
    mail.send(msg)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.generator'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_data = mongo.db.users.find_one({'username': username})

        if user_data:
            user = User(user_data)
            if user.check_password(password):
                login_user(user)
                return redirect(url_for('admin.home'))
        
        flash('Invalid username or password')

    return render_template('login.html')

@auth_bp.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('admin.generator'))
    if request.method == 'POST':
        email = request.form.get('email')
        user_data = mongo.db.users.find_one({'email': email})
        if user_data:
            user = User(user_data)
            send_reset_email(user)
            flash('An email has been sent with instructions to reset your password.')
            return redirect(url_for('auth.login'))
        flash('There is no account with that email. You must register first.')
    return render_template('reset_request.html')

@auth_bp.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('admin.generator'))
    user_data = User.verify_reset_token(token)
    if user_data is None:
        flash('That is an invalid or expired token')
        return redirect(url_for('auth.reset_request'))
    
    if request.method == 'POST':
        new_password = request.form.get('password')
        hashed_password = generate_password_hash(new_password)
        mongo.db.users.update_one({'_id': user_data['_id']}, {'$set': {'password_hash': hashed_password}})
        flash('Your password has been updated! You are now able to log in.')
        return redirect(url_for('auth.login'))
    return render_template('reset_token.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))