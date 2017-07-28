"""
Multithreaded general purpose scraper for brainyquotes.com
"""
import json
import sys
import threading
import time
from collections import defaultdict
from queue import Queue
import requests
from bs4 import BeautifulSoup
from progressbar import progress
import keywords

class ScrapeKeyword(object):
    """docstring for ScrapeKeyword"""
    def __init__(self, keyword, num_pages):
        self.keyword = keyword
        self.num_pages = num_pages
        self.url = 'http://brainyquote.com/search_results.html?q={}'.format(keyword)
        self.lock = threading.Lock()

    def scrape_first_page(self):
        """Initializes scraping and gets first url page based on search word"""
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, 'lxml')
        quotes = soup.select('#quotesList a')
        return quotes

    def multi_scrape_quotes(self, page_number, results):
        """Scrape brainyquotes based on search result multithreaded"""
        try:
            parameters = {"typ":"search", "langc":"en", "ab":"b", "pg":page_number, "id":self.keyword, "m":0}
            response = requests.post(self.url, params=parameters) # Get all search results
            soup = BeautifulSoup(response.content, 'lxml')
            with self.lock:
                results += soup.select('#quotesList a')
        except requests.exceptions.RequestException:
            return

    def multi_scrape(self):
        """Multithreaded scrape implementation"""
        results = self.scrape_first_page()
        threads = [threading.Thread(target=self.multi_scrape_quotes, args=(page, results, )) for page in range(2, self.num_pages + 1)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        return results

def run_queue(que, all_dict, page_range):
    """Utilize Queue for multithreaded scraping"""
    while True:
        topic = que.get()
        if topic is None:
            break
        one_topic_obj = ScrapeKeyword(topic, page_range)
        all_dict[topic] = format_quotes(one_topic_obj.multi_scrape())
        que.task_done()

def scrape_all(scrape_list, page_range):
    """Scrape all contents in list"""
    if len(scrape_list) < 20:
        num_threads = len(scrape_list)
    else:
        num_threads = 20 #optimal number of threads
    que = Queue()
    all_results = {}
    for topic in scrape_list:
        que.put(topic)
    for i in range(num_threads):
        worker = threading.Thread(target=run_queue, args=(que, all_results, page_range))
        worker.daemon = True
        worker.start()
        time.sleep(1)
        progress(i, num_threads, status=' Scraping...')
    que.join()
    return all_results

def format_quotes(quotes):
    """Format quotes to a dict"""
    quotes_list = []
    authors_list = []
    result = defaultdict(set)
    for quote in quotes:
        if quote.get('title') == 'view quote':
            quotes_list.append(quote.text)
        if quote.get('title') == 'view author':
            authors_list.append(quote.text)
    for author, quote in zip(authors_list, quotes_list):
        result[author].add(quote)
    result = dict(result)
    for key, value in result.items():
        result[key] = list(value)
    return dict(result)

def output_json(input_quotes, name):
    """outputs and prettifys quotes to json file"""
    filename = './' + name + '.json'
    json.dump(input_quotes, open(filename, 'w'), indent=4, sort_keys=True)
    print('\nQuotes outputted to ' + name + '.json')

def validate_name(name):
    """Return True if valid name, else return False"""
    bad_chars = ['.', "\\", "/", "*", "?", '"', "<", ">", "|"]
    if any(i in name for i in bad_chars):
        print('Filename cannot contain these characters: ' + '[ ' + ', '.join(bad_chars) + ' ]')
        return False
    return True

if __name__ == '__main__':
    ALL_TOPICS = keywords.AUTHORS
    FILENAME = sys.argv[1]
    START = time.time()
    output_json(scrape_all(ALL_TOPICS, 20), FILENAME) if validate_name(FILENAME) else sys.exit()
    END = time.time()
    
    print('Time taken to scrape: {0:.2f} seconds'.format(END - START))
