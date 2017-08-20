""" Utility functions for webscraper"""
import time
import sys
import json
import progressbar
import keywords
from quote_scraper import ScrapeKeyword

def output_json(input_quotes, name):
    """Outputs and prettifys quotes to json file"""
    filename = './' + name + '.json'
    json.dump(input_quotes, open(filename, 'w'), indent=4, sort_keys=True)
    print('\nQuotes are in ' + name + '.json')

def validate_name(name):
    """Return True if valid name, else return False"""
    bad_chars = ['.', "\\", "/", "*", "?", '"', "<", ">", "|"]
    if any(i in name for i in bad_chars):
        print('Filename cannot contain these characters: ' + '[ ' + ', '.join(bad_chars) + ' ]')
        return False
    return True

def main():
    """Main function to run the program; called in main.py"""
    file = sys.argv[1]
    list_to_scrape = sys.argv[2]
    flag = int(sys.argv[3])
    to_scrape = getattr(keywords, list_to_scrape)
    spinner = progressbar.Spinner()
    start = time.time()
    print('Scraping... ')
    spinner.start()
    if validate_name(file):
        output_json(input_quotes=ScrapeKeyword.scrape_all(scrape_list=to_scrape, page_range=20, flag_topic=flag), name=file)
    else:
        sys.exit()
    spinner.stop()
    end = time.time()
    print('Done!')
    print('Time taken to scrape: {0:.2f} seconds'.format(end - start))
