from flask import Blueprint
from flask_login import UserMixin

from extensions import db

model = Blueprint('model', __name__)

class Product(db.Model):
    asin = db.Column(db.String,primary_key = True)
    name = db.Column(db.String(50))
    category = db.Column(db.String)
    price = db.Column(db.Numeric(10,2))
    last_scraped = db.Column(db.DateTime,nullable=True)

# UserMixin will add Flask-Login attributes to the model so that Flask-Login will be able to work with it
class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String)
    name = db.Column(db.String(1000))

class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rotate_proxy = db.Column(db.Boolean)
    fetch_proxies = db.Column(db.Integer)
    rotating_proxy_page_retry = db.Column(db.Integer)
    no_of_concurrent_request = db.Column(db.Integer)
    download_delay = db.Column(db.Integer)
    download_timeout = db.Column(db.Integer)
    no_of_pg_crawl = db.Column(db.Integer)
    no_of_retry = db.Column(db.Integer)

class Directory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    input_filepath = db.Column(db.String)
    output_filepath = db.Column(db.String)
    consolidated_filepath = db.Column(db.String)
    log_filepath = db.Column(db.String)
    tracker_filepath = db.Column(db.String)
