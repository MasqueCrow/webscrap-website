from flask import Flask, render_template,request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/loreal_db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column('student_id',db.Integer,primary_key = True)
    name = db.Column(db.String(50))
    price = db.Column(db.Float(precision=2))
    last_scraped = db.Column(db.DateTime)

def __init__(self,name,price,last_scraped):
    self.name = name
    self.price = price
    self.last_scraped = last_scraped

@app.route('/')
def index():
    return render_template("index.html")
