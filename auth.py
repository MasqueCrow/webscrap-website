from flask import Blueprint,render_template,redirect, url_for, request,flash
from werkzeug.security import generate_password_hash, check_password_hash
from model import User
from model import db

auth = Blueprint('auth', __name__)

@auth.route('/signup',methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    #if this returns a user, then email already exists in database
    user = User.query.filter_by(email=email).first()

    #if a user is found, we want to redirect back to signup page so user can try again
    if user:
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    new_user = User(email=email, name= name, password=generate_password_hash(password,method='sha256'))

    #add new user to database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/logout')
def logout():
    return 'Logout'
