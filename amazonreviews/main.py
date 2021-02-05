import main_func as m


if __name__ == "__main__":
    # create urls to scrape reviews and products from a csv containing product ASINs
    m.create_urls()

    # Scrape reviews
    # TODO: Update to include rotation for googlebots2.1 in the useragents (See documentation)
    m.get_reviews()
    m.get_outstanding_reviews()
    m.combine_reviews((args.output_dir + '/reviews'), (args.final_output + '/reviews'))

    #  Scrape products
    #  TODO: Update to include rotation for googlebots2.1 in the useragents (See documentation)
    m.get_products()
    m.get_outstanding_products()
    m.combine_products((args.output_dir + '/products'), (args.final_output + '/products'))

    # Obtain profile urls from scraped reviews in raw
    m.get_profile_urls()

    # Scrape profiles
    m.get_profiles()
    m.get_outstanding_profiles()
    m.combine_profiles((args.output_dir + '/profiles'), (args.final_output + '/profiles'))

    # Upload consolidated CSVs into GBQ
    #upload_consolidated_csvs('./credential_file.json', 'crafty-chiller-276910', 'scraped_items_test' )

    ## TODO: CLEAR ALL OUTPUT / INPUT FOLDERS after upload

    # # TODO: Add arguments/config to allow changing of settings.py settings --> take in params from website
    # # TODO: Update readme to include usage examples, parameter explanation and installation instructions
