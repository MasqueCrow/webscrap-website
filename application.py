from flask_login import login_required, current_user
from flask import Flask, render_template,request, jsonify
from amazonreviews import main_func as m

from datetime import datetime
import time
import os

import json
import threading

from extensions import db
from extensions import migrate
from extensions import login_manager

from auth import auth as auth_blueprint
from model import model as model_blueprint

from celery import Celery
from celery_once import QueueOnce


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    return celery

def create_app():
    app = Flask(__name__)
    app.secret_key = 'need to set os env variable for value'
    with app.app_context():
        #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://///Users/jiaweitchea/desktop/fyp/webscrap/loreal_db.sqlite3'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://///mnt/c/users/ryan/work_ryan/y4s1/fyp/webscrap-website/loreal_db.sqlite3'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.secret_key = os.urandom(24)

        #Celery configuration
        app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
        app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
        app.config['CELERY_CREATE_MISSING_QUEUES'] = True

        db.init_app(app)
        migrate.init_app(app,db)
        login_manager.init_app(app)

        app.register_blueprint(auth_blueprint)
        app.register_blueprint(model_blueprint)
    return app

def __init__(self,name,price,last_scraped):
    self.name = name
    self.price = price
    self.last_scraped = last_scraped


def configure_setting(app):
    with app.app_context():
        from model import Setting
        obj = db.session.query(Setting).order_by(Setting.id.desc()).first()

        rotate_proxy = obj.rotate_proxy
        fetch_proxies = obj.fetch_proxies
        rotating_proxy_page_retry = obj.rotating_proxy_page_retry
        no_of_concurrent_request = obj.no_of_concurrent_request
        download_delay = obj.download_delay
        download_timeout = obj.download_timeout
        no_of_retry = obj.no_of_retry
        tracker_output = obj.tracker_filepath

        configure_setting = {
        'RETRY_TIMES': no_of_retry,
        'CONCURRENT_REQUESTS': no_of_concurrent_request,
        'DOWNLOAD_DELAY': download_delay,
        'DOWNLOAD_TIMEOUT': download_timeout,
        'NUMBER_OF_PROXIES_TO_FETCH': fetch_proxies ,
        'ROTATING_PROXY_PAGE_RETRY_TIMES': rotating_proxy_page_retry,
        'ROTATED_PROXY_ENABLED': rotate_proxy,
        'tracker_output' : tracker_output
        }

    return configure_setting

app = create_app()
celery = make_celery(app)

#A user loader tells Flask-Login how to find a specific user from the ID that is stored in their session cookie
login_manager.login_view = 'auth.login'
@login_manager.user_loader
def load_user(user_id):
    from model import User
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))


def check_non_empty_space_in_val(input):
    if input and not input.isspace():
        return True
    return False

@celery.task()
def query_reviews():
    from google.cloud import bigquery
    from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
    from PIL import Image
    import matplotlib.pyplot as plt
    import numpy as np


    project = 'crafty-chiller-276910'
    cwd = os.getcwd()
    #change secret key path based on where you store it
    secret_key_path = os.path.join(cwd,'..','fyp_secret_key.json')

    #initialize bq client
    client = bigquery.Client.from_service_account_json(secret_key_path)

    query = '''
            SELECT cleaned_text
            FROM `crafty-chiller-276910.cleaned_items.reviews`
            '''

    start = time.time()
    query_job = client.query(query)
    print("Time taken to query:",time.time() - start)

    #Convert query to list type
    result_query = list(query_job.result())

    reviews = " "

    start = time.time()

    #Concatenate all reviews to string format
    for i in range(len(result_query)):
        review = result_query[i][0]
        if review is not None:
            reviews += review

    #Remove stop words to refine review text
    stopwords = ['en' ,'tous' ,'ca' ,'le' ,'also', 'im', 'like', 'wa', 'ha', 'tey','est','go','doe','give']
    preprocessed_text = reviews.split()
    resultwords  = [word for word in preprocessed_text if word.lower() not  in stopwords and word.isnumeric() == False]
    result = ' '.join(resultwords)

    #Generate Review wordcloud
    alice_mask = np.array(Image.open(cwd +'/static/img/alice3.jpg'))

    wordcloud = WordCloud(background_color='white',
                      mask=alice_mask,contour_width=1.5, contour_color='steelblue').generate(result)

    image_output_path = cwd +'/static/img/alice.jpg'
    wordcloud.to_file(image_output_path)
    print("Time taken to generate wordcloud:",time.time() - start)

@app.route('/dashboard')
@login_required
def index():
    #create link to navigate back to  webscrape status
    query_reviews.apply_async(queue='queue3')

    #Read time-series graph values
    f = open('webscrape_counter.json', 'r+')
    webscrape_data = json.load(f)

    #stringify json value
    webscrape_data = json.dumps(webscrape_data)

    return render_template("dashboard.html",name=current_user.name,url ='/static/img/alice.jpg',webscrape_data=webscrape_data)


@app.route('/webscrape')
@login_required
def webscrape():
    from model import Product
    products = Product.query.all()
    return render_template("webscrape.html",name=current_user.name,products=products)

#Clear content of counter file at the beginning of running webscrape tool
def clear_file(filepath,filename):
    open(filepath+filename,'w').close()

# Update counter of web scrape tool each time it is activated (queue 1 with get_review_profile)
def update_counter_file():
    # get current date
    current_date = datetime.today().strftime('%Y-%m-%d')

    # load json counter file to read/write to
    with open('webscrape_counter.json', 'r+') as infile:
        # load current file unless it is empty which causes the jsondecode error
        try:
            current_counts = json.load(infile)
            print("JSON WEBSCRAPE COUNTER FILE LOADED SUCCESSFULLY", current_counts)
            if current_date in current_counts:
                current_counts[f'{current_date}'] += 1
            else:
                current_counts[f'{current_date}'] = 1
        except ValueError: #catches json decode error
            # initialize the first time when the json counter file is empty
            print("JSON WEBSCRAPE COUNTER FILE NOT LOADED DUE TO VALUE ERROR")
            current_counts = {}
            current_counts[f'{current_date}'] = 1
        with open('webscrape_counter.json', 'w') as outfile:
            # write updated count to counter file
            json.dump(current_counts, outfile)
            infile.close()
            outfile.close()

def update_product_scrapetime():
    from datetime import datetime
    from model import Product

    #Retrieve crawled asin from review file in crawl_progress folder
    asins = set()
    with open('crawl_progress/review.txt','r') as f:
        for url in f:
            asin = url.split("/")[-2]
            asins.add(asin)

    if 'product-reviews' in asins:
        asins.remove('product-reviews')

    #Iterate asins to update last_scraped of products
    for asin in asins:
        last_scraped = datetime.now()
        product = Product.query.filter_by(asin= asin).first()
        product.last_scraped = last_scraped
        db.session.commit()
        print("product:",product,"time:",product.last_scraped )


#update scrape task to be true when celery task has been completed
def update_status(task):
    with open('./crawl_progress/status.txt','a') as f:
        f.write(task + ",")

@celery.task()
def get_review_profile(config,com_review_output_path,com_review_con_path,com_profile_output_path, com_profile_con_path):
    clear_file('./crawl_progress/','review.txt')
    clear_file('./crawl_progress/','profile.txt')
    update_counter_file()

    m.get_reviews(config)
    m.get_outstanding_reviews(config)
    m.update_outstanding_reviews(config)
    m.combine_reviews(com_review_output_path, com_review_con_path)

    #Update review status when crawling has been completed
    update_status('review')

    #update datetime of products that have been scraped
    update_product_scrapetime()

    # Obtain profile urls from scraped reviews in raw
    m.get_profile_urls(config)

    # Scrape profiles
    m.get_profiles(config)
    m.get_outstanding_profiles(config)
    m.update_outstanding_profiles(config)
    m.combine_profiles(com_profile_output_path, com_profile_con_path)

    #Update profile status when crawling has been completed
    update_status('profile')

@celery.task()
def get_product(config,com_product_output_path, com_product_con_path):
    clear_file('./crawl_progress/','product.txt')
    m.get_products(config)
    m.get_outstanding_products(config)
    m.update_outstanding_products(config)
    m.combine_products(com_product_output_path, com_product_con_path)

    #Update product status when crawling has been completed
    update_status('product')

# @celery.task()
# def upload_items_and_clean_output_folder(config):
#     cwd = os.getcwd()
#     #change secret key path based on where you store it
#     secret_key_path = os.path.join(cwd,'credential_file.json')
#     m.upload_consolidated_csvs(secret_key_path, 'crafty-chiller-276910', 'scraped_items_test', config)
#     m.clear_output_folders(config)

review_url_count = 0
profile_url_count = 0
product_url_count = 0
###################################################
@app.route('/scrapeproduct',methods=['POST'])
@login_required
def scrape_product():

    from model import Setting

    #Retrieve last record in setting model
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

    from model import Product

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

    #paths for combine_profile parameters
    com_profile_output_path = os.path.join(combined_output_basepath, 'profiles')
    com_profile_con_path = os.path.join(combined_con_basepath,'profiles')

    #clear status in status file which checks for celery task completion
    clear_file('./crawl_progress/','status.txt')

    #invoke review and profile celery task (reviews ->profile)
    get_review_profile.apply_async(queue='queue1',args=(config,com_review_output_path,com_review_con_path,com_profile_output_path, com_profile_con_path))

    #paths for combine_products parameters
    com_product_output_path = os.path.join(combined_output_basepath, 'products')
    com_product_con_path = os.path.join(combined_con_basepath,'products')

    #invoke product celery task
    get_product.apply_async(queue='queue2',args=(config,com_product_output_path,com_product_con_path))

    msg = "Webscrape tool has been successfully activated. It might take a while before web crawling is completed. Please check back again later."

    return render_template("webscrape_progress.html",name=current_user.name,msg=msg,review_url_count = review_url_count,profile_url_count=profile_url_count,product_url_count=product_url_count)

def status_result():
    f = open('./crawl_progress/status.txt','r')
    result = f.read()
    result = result[:-1].split(",")
    return result

@app.route('/webscrapestatus',methods=['GET','POST'])
@login_required
def webscrapestatus():

    global review_url_count
    global profile_url_count
    global product_url_count

    review_url_count = sum(1 for line in open('./crawl_progress/review.txt'))
    profile_url_count = sum(1 for line in open('./crawl_progress/profile.txt'))
    product_url_count = sum(1 for line in open('./crawl_progress/product.txt'))


    msg = "Webscrape tool has been successfully activated. It might take a while before web crawling is completed. Please check back again later."
    complete_msg = ""
    config = {
    "con_path": "output/consolidated",
    "output_path": "output/raw",
    "log_path": "output/logs/"
    }

    result = status_result()

    if len(result) == 3:
        complete_msg = "Web scraping has been completed."
        #invoke upload consolidated csvs and recreate output folder task after queue 1 and queue2
        cwd = os.getcwd()
        #change secret key path based on where you store it
        secret_key_path = os.path.join(cwd,'credential_file.json')
        m.upload_consolidated_csvs(secret_key_path, 'crafty-chiller-276910', 'scraped_items_test', config)
        m.clear_output_folders(config)

    print("check status:",result)

    return render_template("webscrape_progress.html",name=current_user.name,
                           review_url_count = review_url_count,
                           profile_url_count=profile_url_count,
                           product_url_count=product_url_count,
                           msg=msg,complete_msg=complete_msg)

#Retrieve last record in db and populate values in settings form
@app.route('/setting')
@login_required
def setting():
    from model import Setting

    #Retrieve last setting record
    obj = db.session.query(Setting).order_by(Setting.id.desc()).first()
    input_path = obj.input_filepath
    output_path = obj.output_filepath
    no_of_pg_crawl = obj.no_of_pg_crawl
    no_of_retry = obj.no_of_retry
    con_path = obj.consolidated_filepath
    log_path = obj.log_filepath
    tracker_path = obj.tracker_filepath

    rotate_proxy = obj.rotate_proxy
    fetch_proxies = obj.fetch_proxies
    rotating_proxy_page_retry = obj.rotating_proxy_page_retry
    no_of_concurrent_request = obj.no_of_concurrent_request
    download_delay = obj.download_delay
    download_timeout = obj.download_timeout

    return render_template(
            "setting.html",name=current_user.name,
            input_path = input_path,
            output_path = output_path,
            no_of_pg_crawl = no_of_pg_crawl,
            no_of_retry = no_of_retry,
            con_path = con_path,
            log_path = log_path,
            tracker_path = tracker_path,
            rotate_proxy = rotate_proxy,
            fetch_proxies = fetch_proxies,
            rotating_proxy_page_retry = rotating_proxy_page_retry,
            no_of_concurrent_request = no_of_concurrent_request,
            download_delay = download_delay,
            download_timeout = download_timeout
            )

@app.route('/webscrapeconfig',methods=['POST'])
@login_required
def insert_setting_record():
    from model import Setting

    input_path = request.form.get('input_path')
    output_path = request.form.get('output_path')
    no_of_pg_crawl = int(request.form.get('no_of_pg_crawl'))
    no_of_retry = int(request.form.get('no_of_retry'))
    con_path = request.form.get('con_path')
    log_path = request.form.get('log_path')
    tracker_path = request.form.get('tracker_path')

    rotate_proxy = bool(request.form.get('rotate_proxy'))
    fetch_proxies = int(request.form.get('fetch_proxies'))
    rotating_proxy_page_retry = int(request.form.get('rotating_proxy_page_retry'))
    no_of_concurrent_request = int(request.form.get('no_of_concurrent_request'))
    download_delay = int(request.form.get('download_delay'))
    download_timeout = int(request.form.get('download_timeout'))

    #display result status of inserting new product into db
    msg = ""

    #Validate inputs are string and integers before inserting records
    if (isinstance(no_of_pg_crawl,int) and isinstance(no_of_retry,int) and
    check_non_empty_space_in_val(input_path) and check_non_empty_space_in_val(output_path) and
    check_non_empty_space_in_val(con_path) and check_non_empty_space_in_val(log_path) and
    check_non_empty_space_in_val(tracker_path) and
    isinstance(fetch_proxies,int) and isinstance(rotating_proxy_page_retry,int) and
    isinstance(no_of_concurrent_request,int) and isinstance(download_delay,int) and
    isinstance(download_timeout,int)):

        new_setting = Setting(input_filepath = input_path,output_filepath = output_path,consolidated_filepath = con_path,
                              log_filepath = log_path,tracker_filepath = tracker_path,no_of_pg_crawl = no_of_pg_crawl,no_of_retry = no_of_retry,
                              rotate_proxy = rotate_proxy, fetch_proxies = fetch_proxies,
                              rotating_proxy_page_retry = rotating_proxy_page_retry,no_of_concurrent_request = no_of_concurrent_request,
                              download_delay = download_delay, download_timeout = download_timeout)


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

@app.route('/newproduct')
@login_required
def create_product():
    return render_template('new_products.html',name=current_user.name)

#from model import db
@app.route('/newproducts',methods=['POST'])
def new_product():
    from model import Product

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
