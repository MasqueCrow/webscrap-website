import csv
import glob
import json
import os
from datetime import datetime
from subprocess import call

from amazonreviews.gcpFunctions import create_bq_client, upload_csv_as_df
from amazonreviews.stitch import combine_products, combine_profiles, combine_reviews

import configargparse
import pandas as pd

import time

#Contains functions imported from main.py

def get_reviews(config):

    """
    This function reads the scrape_reviews.csv and runs the amazon_reviews spider in batches of product url and pages.
    """
    basepath = os.path.dirname(__file__)

    input_path = os.path.join(basepath,config['input_path'], "scrape_reviews.csv")
    output_dir = os.path.join(basepath,config['output_path'],"reviews")
    log_output = os.path.join(basepath,config['log_path'] ,'outstanding_reviews.csv')

    url_df = pd.read_csv(input_path)
    for ind, row in url_df.iterrows():

        curr_url = row['url']
        curr_asin = curr_url.split('/')[4]

        output_path = output_dir + "/reviews_{}.csv".format(curr_asin)

        cmd = 'scrapy runspider '+ basepath + '/spiders/amazon_reviews.py -o {} -a config="{},{},{}"'.format(output_path, curr_url, log_output, "main")
        call(cmd, shell=True)


def get_outstanding_reviews(config):
    """
    Retries crawling the outstanding reviews that were unable to be retrieved in get_reviews. Updates the outstanding
    logs after every try.
    """
    basepath = os.path.dirname(__file__)

    log_output = os.path.join(basepath,config['log_path'],"outstanding_reviews.csv")
    output_dir = os.path.join(basepath,config['output_path'],"reviews")
    num_retry = int(config['no_of_retry'])
    print("log:",log_output)
    cnt = 0

    while cnt < num_retry:
        cnt += 1
        print("Retrying outstanding: {iter}".format(iter=cnt))
        # Scrape remaining urls which failed previously
        output_path = output_dir + "/reviews_outstanding.csv"

        print(output_path)
        print(log_output)

        cmd = 'scrapy runspider '+ basepath + '/spiders/amazon_reviews.py -o {} -a config="{},{},{}"'.format(output_path, "NA", log_output, "outstanding")
        call(cmd, shell=True)

        # Update those urls which are scraped or not (0 or 1 in scraped column)
        updated_df = pd.read_csv(log_output)

        outstanding_df = updated_df.groupby('url').filter(lambda x: len(x) > 1)
        outstanding_df = outstanding_df.drop_duplicates('url', keep='last')
        cleared_df = updated_df.groupby('url').filter(lambda x: len(x) == 1)
        cleared_df['scraped'] = 1
        updated_df = pd.concat([cleared_df, outstanding_df])
        updated_df.to_csv(log_output, index=False)


def get_outstanding_profiles(config):
    """
    Retries crawling the outstanding profiles that were unable to be retrieved in get_profiles. Updates the outstanding
    logs after every try.
    """
    basepath = os.path.dirname(__file__)
    log_output = os.path.join(basepath,config['log_path'],"outstanding_profiles.csv")
    output_dir = os.path.join(basepath,config['output_path'],"profiles")
    num_retry = int(config['no_of_retry'])

    cnt = 0
    while cnt < num_retry:
        cnt += 1
        print("Retrying outstanding: {iter}".format(iter=cnt))
        # Scrape remaining profiles which failed previously
        output_path = output_dir + "/profiles_outstanding.csv"

        cmd = 'scrapy runspider spiders/amazon_profiles.py -o {out_path} -a config="_,{log_output},_,_,outstanding"' \
            .format(out_path=output_path, log_output=log_output)
        call(cmd, shell=True)

        # Update those urls which are scraped or not
        updated_df = pd.read_csv(log_output)
        outstanding_df = updated_df.groupby('url').filter(lambda x: len(x) > 1)
        outstanding_df = outstanding_df.drop_duplicates('url', keep='last')
        cleared_df = updated_df.groupby('url').filter(lambda x: len(x) == 1)
        cleared_df['scraped'] = 1
        updated_df = pd.concat([cleared_df, outstanding_df])

        updated_df.to_csv(log_output, index=False)


def get_outstanding_products(config):
    """
    Retries crawling the outstanding products that were unable to be retrieved in get_products. Updates the outstanding
    logs after every try.
    """

    basepath = os.path.dirname(__file__)
    log_output = os.path.join(basepath,config['log_path'],'outstanding_products.csv')
    output_dir = os.path.join(basepath,config['output_path'],'products')
    num_retry = int(config['no_of_retry'])

    cnt = 0
    while cnt < num_retry:
        cnt += 1
        print("Retrying outstanding: {iter}".format(iter=cnt))
        # Scrape remaining profiles which failed previously
        output_path = output_dir + "/products_outstanding.csv"

        cmd = 'scrapy runspider '+ basepath + '/spiders/amazon_products.py -o {out_path} -a config="_,{log_output},_,_,outstanding"' \
            .format(out_path=output_path, log_output=log_output)
        call(cmd, shell=True)

        # Update those urls which are scraped or not
        updated_df = pd.read_csv(log_output)
        outstanding_df = updated_df.groupby('url').filter(lambda x: len(x) > 1)
        outstanding_df = outstanding_df.drop_duplicates('url', keep='last')
        cleared_df = updated_df.groupby('url').filter(lambda x: len(x) == 1)
        cleared_df['scraped'] = 1
        updated_df = pd.concat([cleared_df, outstanding_df])

        updated_df.to_csv(log_output, index=False)


def get_profiles(config):
    """
    This function reads the scrape_profiles.csv and runs the amazon_product spider in batches
    """

    basepath = os.path.dirname(__file__)
    profiles_path = os.path.join(basepath,config['input_path'],'scrape_profiles.csv')
    log_output =  os.path.join(basepath,config['log_path'],'outstanding_profiles.csv')
    output_dir = os.path.join(basepath,config['output_path'],'profiles')
    profiles_df = pd.read_csv(profiles_path)
    freq = 200
    max_rows = profiles_df.shape[0] + 1

    for start_row in range(0, max_rows, freq):
        end_row = min(start_row + freq, max_rows)

        output_path = output_dir + '/profiles_{time}_{s_row}_{e_row}.csv'\
            .format(s_row=start_row, e_row=end_row, time=datetime.now().strftime("%H%M%S"))

        cmd = 'scrapy runspider ' + basepath + '/spiders/amazon_profiles.py -o {output_path} '\
              '-a config="{profiles_path},{log_file},{s_row},{e_row},main"' \
            .format(output_path=output_path, profiles_path=profiles_path, log_file=log_output, s_row=start_row, e_row=end_row, time=datetime.now().strftime("%H%M%S"))
        call(cmd, shell=True)


def get_products(config):
    """
    This function reads the scrape_products.csv and runs the amazon_product spider in batches
    """

    basepath = os.path.dirname(__file__)
    products_path = os.path.join(basepath,config['input_path'],'scrape_products.csv')
    log_output = os.path.join(basepath,config['log_path'],'outstanding_products.csv')
    output_dir = os.path.join(basepath,config['output_path'],"products")
    products_df = pd.read_csv(products_path)

    freq = 200
    max_rows = products_df.shape[0] + 1
    for start_row in range(0, max_rows, freq):
        end_row = min(start_row + freq, max_rows)
        output_path = output_dir + '/products_info_{time}_{s_row}_{e_row}.csv'\
            .format(s_row=start_row, e_row=end_row, time=datetime.now().strftime("%H%M%S"))

        cmd = 'scrapy runspider ' + basepath + '/spiders/amazon_products.py -o {output_path} '\
              '-a config="{products_path},{log_file},{s_row},{e_row},main"'\
            .format(output_path=output_path, log_file=log_output, products_path=products_path, s_row=start_row, e_row=end_row)
        call(cmd, shell=True)


def create_urls(asins):
    """
    This function creates the amazon urls for scraping reviews and products from a csv containing
    amazon product ASINs.
    """
    #Find user's basepath and add relative file path. Remove specifying hard absolute filepath
    basepath = os.path.dirname(__file__)

    #asin_file_path = os.path.join(basepath,'data','product_asin.csv')
    product_file_path = os.path.join(basepath,'data','scrape_products.csv')
    review_file_path = os.path.join(basepath,'data','scrape_reviews.csv')

    product_urls = [f"https://www.amazon.com/dp/{asin}" for asin in asins]
    review_urls = [f"https://www.amazon.com/product-reviews/{asin}/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews&sortBy=recent" for asin in asins]

    product_df = pd.DataFrame(product_urls, columns=["url"])
    product_df.to_csv(product_file_path, index=False)

    review_df = pd.DataFrame(review_urls, columns=["url"])
    review_df.to_csv(review_file_path, index=False)

def get_profile_urls(config):
    """
    This function creates the amazon urls for scraping profiles from the scraped reviews that are stored
    in the output/raw folder.
    """

    basepath = os.path.dirname(__file__)
    reviews_file_path = os.path.join(basepath,config['con_path'],'reviews')
    profiles_path =  os.path.join(basepath,config['input_path'],'scrape_profiles.csv')

    # read all reviews in file path into one df
    all_files = glob.glob(os.path.join(reviews_file_path, "*.csv"))    # advisable to use os.path.join as this makes concatenation OS independent
    df_from_each_file = (pd.read_csv(f) for f in all_files)
    concatenated_df = pd.concat(df_from_each_file, ignore_index=True)

    # remove rows with empty profile links if it exists (profile that left the review might have been removed or deleted)
    concatenated_df = concatenated_df.dropna(subset=['profile_link'])
    # extract profile_links column from concatenated df
    profile_links = concatenated_df.profile_link.tolist()
    # remove duplicate profile links
    distinct_profile_links = (set(profile_links))

    # generate profile urls to scrape
    profile_urls = [f"https://www.amazon.com{profile_link}" for profile_link in distinct_profile_links]
    profile_df = pd.DataFrame(profile_urls, columns=["url"])
    profile_df.to_csv(profiles_path, index=False)

def upload_consolidated_csvs(svc_account_credential_file_path, project_name, target_dataset, config):
    """
    This function uploads the consolidated scraped items into GBQ.
    Change credential file path / table names accordingly as needed
    """
    # project parameters
    basepath = os.path.dirname(__file__)
    consolidated_dir = os.path.join(basepath,config['con_path'])

    ## upload reviews
    reviews_file_path = consolidated_dir + ("/reviews/consolidated_reviews.csv")
    # add try-except logic in case consolidated file does not exist
    try:
        # upload if file > 1kb
        if os.stat(reviews_file_path).st_size > 1000:
            upload_csv_as_df(svc_account_credential_file_path, project_name, target_dataset, "reviews", reviews_file_path)
        else:
            print("There is no reviews in the consolidated file to be uploaded")
    except FileNotFoundError:
        print(f"{reviews_file_path} does not exist")


    ## upload products
    products_file_path = consolidated_dir + ("/products/consolidated_products.csv")
    # add try-except logic in case consolidated file does not exist
    try:
        if os.stat(products_file_path).st_size > 1000:
            upload_csv_as_df(svc_account_credential_file_path, project_name, target_dataset, "products", products_file_path)
        else:
            print("There is no products in the consolidated file to be uploaded")
    except FileNotFoundError:
        print(f"{products_file_path} does not exist")

    ## upload profiles
    profiles_file_path = consolidated_dir + ("/profiles/consolidated_profiles.csv")
    # add try-except logic in case consolidated file does not exist
    try:
        if os.stat(profiles_file_path).st_size > 1000:
            upload_csv_as_df(svc_account_credential_file_path, project_name, target_dataset, "profiles", profiles_file_path)
        else:
            print("There is no profiles in the consolidated file to be uploaded")
    except FileNotFoundError:
        print(f"{profiles_file_path} does not exist")

def clear_output_folders(config):
    """
    This function helps to clear all the output folders of the csv files and then recreates the outstanding item files
    in the log folder with the headers - 'url', 'num_items' and 'scraped'
    """
    basepath = os.path.dirname(__file__)
    raw_output_path = os.path.join(basepath,config['output_path'])
    output_path = raw_output_path.split("/raw")[0]
    glob_exp = output_path + "/**/*.csv"
    # remove csv files in output folder and its sub-folders recursively
    files = glob.glob(glob_exp, recursive=True)
    for f in files:
        try:
            os.remove(f)
        except OSError as e:
            print("Error: %s : %s" % (f, e.strerror))
    print("csv files in output folder have been removed")

    # recreate csv files in log folder
    file_path = os.path.join(basepath,config['log_path'])
    file_names = ['outstanding_reviews.csv','outstanding_profiles.csv','outstanding_products.csv']
    for fn in file_names:
        csv_name = file_path + fn
        with open(csv_name, 'w') as csvfile:
            fieldnames = ['url', 'num_items', 'scraped']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
    print(f"log files with headers have been created in {file_path} folder")

def update_outstanding_reviews(config):
    basepath = os.path.dirname(__file__)
    log_output = os.path.join(basepath,config['log_path'],'outstanding_reviews.csv')
    log_counter = os.path.join(basepath,config['log_path'], "outstanding_items.json")

    # Update those urls which are scraped or not
    updated_df = pd.read_csv(log_output)
    number_of_rows = len(updated_df.index)

    with open(log_counter, 'r') as infile:
        outstanding_items = json.load(infile)
        outstanding_items['reviews'] = number_of_rows
        with open(log_counter, 'w') as outfile:
            json.dump(outstanding_items, outfile)

def update_outstanding_profiles(config):
    basepath = os.path.dirname(__file__)
    log_output = os.path.join(basepath,config['log_path'],'outstanding_profiles.csv')
    log_counter = os.path.join(basepath,config['log_path'], "outstanding_items.json")

    # Update those urls which are scraped or not
    updated_df = pd.read_csv(log_output)
    number_of_rows = len(updated_df.index)

    with open(log_counter, 'r') as infile:
        outstanding_items = json.load(infile)
        outstanding_items['profiles'] = number_of_rows
        with open(log_counter, 'w') as outfile:
            json.dump(outstanding_items, outfile)

def update_outstanding_products(config):
    basepath = os.path.dirname(__file__)
    log_output = os.path.join(basepath,config['log_path'],'outstanding_products.csv')
    log_counter = os.path.join(basepath,config['log_path'], "outstanding_items.json")

    # Update those urls which are scraped or not
    updated_df = pd.read_csv(log_output)
    number_of_rows = len(updated_df.index)

    with open(log_counter, 'r') as infile:
        outstanding_items = json.load(infile)
        outstanding_items['products'] = number_of_rows
        with open(log_counter, 'w') as outfile:
            json.dump(outstanding_items, outfile)
