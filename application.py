from flask import Flask, render_template,request
import os
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://///Users/jiaweitchea/desktop/fyp/webscrap/loreal_db.sqlite3'
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
from model import Setting

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

#A user loader tells Flask-Login how to find a specific user from the ID that is stored in their session cookie
@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))

from flask_login import login_required, current_user

def check_non_empty_space_in_val(input):
    if input and not input.isspace():
        return True
    return False


@app.route('/dashboard')
@login_required
def index():
    return render_template("dashboard.html",name=current_user.name)


@app.route('/webscrape')
@login_required
def webscrape():
    products = Product.query.all()

    return render_template("webscrape.html",name=current_user.name,products=products)

#ML model integration
import json
from amazonreviews import main_func as m


@app.route('/scrapeproduct',methods=['POST'])
def scrape_product():
    #Retrieve last setting record
    obj = db.session.query(Setting).order_by(Setting.id.desc()).first()
    input_path = obj.input_filepath
    output_path = obj.output_filepath
    no_of_pg_crawl = obj.no_of_pg_crawl
    no_of_retry = obj.no_of_retry
    con_path = obj.consolidated_filepath
    log_path = obj.log_filepath

    config = {
        'input_path': input_path,
        'output_path': output_path,
        'no_of_pg_crawl': no_of_pg_crawl,
        'no_of_retry': no_of_retry,
        'con_path': con_path,
        'log_path': log_path
    }

    #Retrieve ASIN from selected products and stored it in a list
    asin_list = []
    if request.method == "POST":
        data = request.form['myJSONArrs']
        data = json.loads(data)
        print(data,type(data))

        for record in data:
            asin = record[1]
            asin_list.append(asin)

    # create urls to scrape reviews and products from a csv containing product ASINs
    m.create_urls(asin_list)

    #Find the basepath to this project folder
    basepath = os.path.dirname(__file__)

    #basepath for all combined funcs (review,product,profile)
    combined_output_basepath = os.path.join(basepath,'amazonreviews',config['output_path'])
    combined_con_basepath = os.path.join(basepath,'amazonreviews',config['con_path'])

    #paths for combine_review parameters
    com_review_output_path = os.path.join(combined_output_basepath, 'reviews')
    com_review_con_path = os.path.join(combined_con_basepath,'reviews')


    # Scrape reviews
    # TODO: Update to include rotation for googlebots2.1 in the useragents (See documentation)
    #m.get_reviews(config)
    #m.get_outstanding_reviews(config)
    #m.combine_reviews(com_review_output_path, com_review_con_path)

    #paths for combine_products parameters
    #com_product_output_path = os.path.join(combined_output_basepath, 'products')
    #com_product_con_path = os.path.join(combined_con_basepath,'products')

    #  Scrape products
    #  TODO: Update to include rotation for googlebots2.1 in the useragents (See documentation)
    #m.get_products(config)
    #m.get_outstanding_products(config)
    #m.combine_products(com_product_output_path, com_product_con_path)


    # Obtain profile urls from scraped reviews in raw
    #m.get_profile_urls(config)

    #paths for combine_review parameters
    com_profile_output_path = os.path.join(combined_output_basepath, 'profiles')
    com_profile_con_path = os.path.join(combined_con_basepath,'profiles')

    # Scrape profiles
    #m.get_profiles(config)
    #m.get_outstanding_profiles()
    #m.combine_profiles(com_profile_output_path, com_profile_con_path)

    return render_template("webscrape.html",name=current_user.name)

@app.route('/setting')
@login_required
def setting():
    #Retrieve last setting record
    obj = db.session.query(Setting).order_by(Setting.id.desc()).first()
    input_path = obj.input_filepath
    output_path = obj.output_filepath
    no_of_pg_crawl = obj.no_of_pg_crawl
    no_of_retry = obj.no_of_retry
    con_path = obj.consolidated_filepath
    log_path = obj.log_filepath



    return render_template(
            "setting.html",name=current_user.name,
            input_path = input_path,
            output_path = output_path,
            no_of_pg_crawl = no_of_pg_crawl,
            no_of_retry = no_of_retry,
            con_path = con_path,
            log_path = log_path
            )


@app.route('/webscrapeconfig',methods=['POST'])
@login_required
def insert_setting_record():
    input_path = request.form.get('input_path')
    output_path = request.form.get('output_path')
    no_of_pg_crawl = int(request.form.get('no_of_pg_crawl'))
    no_of_retry = int(request.form.get('no_of_retry'))
    con_path = request.form.get('con_path')
    log_path = request.form.get('log_path')

    #display result status of inserting new product into db
    msg = ""

    #Validate inputs are string and integers before inserting records
    if (isinstance(no_of_pg_crawl,int) and isinstance(no_of_retry,int) and
    check_non_empty_space_in_val(input_path) and check_non_empty_space_in_val(output_path) and
    check_non_empty_space_in_val(con_path) and check_non_empty_space_in_val(log_path) ):

        new_setting = Setting(input_filepath = input_path,output_filepath = output_path,consolidated_filepath=con_path,log_filepath=log_path,no_of_pg_crawl = no_of_pg_crawl,no_of_retry = no_of_retry)

        #add new record setting to database
        db.session.add(new_setting)
        db.session.commit()

        msg = "All webscrap variables have been successfully added to the database."

    else:
        msg = "Failed to insert variable configs into database."


    return render_template('setting_status.html',msg=msg,name=current_user.name)

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
    asin =request.form.get('asin')
    name = request.form.get('name')
    category = request.form.get('category')
    price = float(request.form.get('price'))
    print("asin:",asin,"name:",name,"cat:",category,"price:",price)


    #display result status of inserting new product into db
    msg = ""

    #check valid value type and string is non-empty/space
    if isinstance(price,float) and isinstance(name,str) and check_non_empty_space_in_val(name) and check_non_empty_space_in_val(asin):
        new_product = Product(asin=asin,name=name,price=price,category=category)

        #add new product to database
        db.session.add(new_product)
        db.session.commit()

        insert_status = "successful"
        msg = name + " of price $"+ str(price) + " has been successfully added to the database."
    else:
        msg = "Failed to insert " + name + " product."

    return render_template('product_status.html',msg=msg,name=name)
