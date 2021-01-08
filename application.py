from flask import Flask, render_template,request
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/loreal_db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.urandom(24)

def __init__(self,name,price,last_scraped):
    self.name = name
    self.price = price
    self.last_scraped = last_scraped

# blueprint for auth routes in our app
from auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

# blueprint for models
from model import model as model_blueprint
app.register_blueprint(model_blueprint)

from flask_login import LoginManager
from model import User


login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

#A user loader tells Flask-Login how to find a specific user from the ID that is stored in their session cookie
@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))

from flask_login import login_required, current_user

@app.route('/dashboard')
@login_required
def index():
    return render_template("dashboard.html",name =current_user.name)
