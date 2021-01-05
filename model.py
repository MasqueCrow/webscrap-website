from flask_login import UserMixin
from application import app
from flask_sqlalchemy import SQLAlchemy
from flask import Blueprint

model = Blueprint('model', __name__)
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column('student_id',db.Integer,primary_key = True)
    name = db.Column(db.String(50))
    price = db.Column(db.Float(precision=2))
    last_scraped = db.Column(db.DateTime)

# UserMixin will add Flask-Login attributes to the model so that Flask-Login will be able to work with it
class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
