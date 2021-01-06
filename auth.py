from flask import Blueprint,render_template,redirect, url_for, request,flash
from flask_login import login_user,logout_user,login_required
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

@auth.route('/login',methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    print(email,password)
    
    user = User.query.filter_by(email=email).first()

    #check if user actually exists
    #take the user-supplied password, harsh it, and compare it to hashed password in database
    if not user or not check_password_hash(user.password,password):
        flash('Please check your login details and try again.')
        #if user doesn't exist or incorrect password,reload page
        return redirect(url_for('auth.login'))

    #if the above check passes, then we know user has right credentials
    login_user(user,remember=remember)
    return redirect(url_for('index'))

@auth.route('/')
def login():
    return render_template('login.html')

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
