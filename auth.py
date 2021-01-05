from flask import Blueprint,render_template

auth = Blueprint('auth', __name__)

@auth.route('/login',methods=['POST'])
def login():
    return render_template('login.html')

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/logout')
def logout():
    return 'Logout'
