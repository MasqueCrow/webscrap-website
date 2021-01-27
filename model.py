from application import app
from flask import Blueprint
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

model = Blueprint('model', __name__)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Product(db.Model):
    id = db.Column('student_id',db.Integer,primary_key = True)
    name = db.Column(db.String(50))
    price = db.Column(db.Numeric(10,2))
    last_scraped = db.Column(db.DateTime,nullable=True)

# UserMixin will add Flask-Login attributes to the model so that Flask-Login will be able to work with it
class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String)
    name = db.Column(db.String(1000))
