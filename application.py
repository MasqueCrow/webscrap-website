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
from model import Product

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
    return render_template("dashboard.html",name=current_user.name)


@app.route('/webscrape')
@login_required
def webscrape():
    products = Product.query.all()

    return render_template("webscrape.html",name=current_user.name,products=products)

@app.route('/setting')
@login_required
def setting():
    return render_template("setting.html",name=current_user.name)

@app.route('/report')
@login_required
def report():
    return render_template("report.html",name=current_user.name)

#internal use, not visible in nav bar
@app.route('/newproduct')
def create_product():
    name = "Admin"
    return render_template('new_products.html',name=name)

from model import db
@app.route('/newproducts',methods=['POST'])
def new_product():
    name = request.form.get('name')
    price = float(request.form.get('price'))

    msg = ""
    #check valid value type and string is non-empty/space
    if isinstance(price,float) and isinstance(name,str) and (name and not name.isspace()) :
        new_product = Product(name=name,price=price)

        #add new product to database
        db.session.add(new_product)
        db.session.commit()

        insert_status = "successful"
        msg = name + " of price $"+ str(price) + " has been successfully added to the database."
    else:
        msg = "Failed to insert " + name + " product."

    return render_template('product_status.html',msg=msg,name=name)
