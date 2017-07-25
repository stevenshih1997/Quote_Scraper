"""
Multithreaded general purpose scraper for brainyquotes.com
"""
import json
import threading
import time
from collections import defaultdict
from queue import Queue
import requests
from bs4 import BeautifulSoup

class ScrapeKeyword(object):
    """docstring for ScrapeKeyword"""
    def __init__(self, keyword, num_pages):
        self.keyword = keyword
        self.num_pages = num_pages
        self.url = 'http://brainyquote.com/search_results.html?q={}'.format(keyword)
        self.lock = threading.Lock()

    def first_scrape(self):
        """Initializes scraping and gets first url page based on search word"""
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, 'lxml')
        quotes = soup.select('#quotesList a')
        return quotes

    def multi_scrape_quotes(self, page_number, results):
        """Scrape brainyquotes based on search result multithreaded"""
        parameters = {"typ":"search", "langc":"en", "ab":"b", "pg":page_number, "id":self.keyword, "m":0}
        response = requests.post(self.url, params=parameters) # Get all search results
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'lxml')
        with self.lock:
            results += soup.select('#quotesList a')

    def multi_scrape(self):
        """Multithreaded scrape implementation"""
        results = self.first_scrape()
        threads = [threading.Thread(target=self.multi_scrape_quotes, args=(i, results, )) for i in range(2, self.num_pages + 1)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        return results

def run_queue(que, all_dict, page_range):
    """Utilize Queue for multithreaded scraping"""
    while True:
        topic = que.get()
        scrape_one_topic_object = ScrapeKeyword(topic, page_range)
        all_dict[topic] = format_quotes(scrape_one_topic_object.multi_scrape())
        que.task_done()

def scrape_all(scrape_list, page_range):
    """Scrape all contents in list"""
    num_threads = len(scrape_list)
    que = Queue()
    all_results = {}
    for topic in scrape_list:
        que.put(topic)
    for _ in range(num_threads):
        worker = threading.Thread(target=run_queue, args=(que, all_results, page_range))
        worker.daemon = True
        worker.start()
        time.sleep(1)
    que.join()
    print('Queue is now empty: ', que.empty())
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

def output_json(input_quotes):
    """outputs and prettifys quotes to json file"""
    json.dump(input_quotes, open('./quotes.json', 'w'), indent=4, sort_keys=True)
    print('File output succeeded')

if __name__ == '__main__':
    SCRAPE_LIST = ['Age', 'Alone', 'Amazing', 'Anger', 'Anniversary', 'Architecture', 'Art', 'Attitude', 'Beauty', 'Best', 'Birthday', 'Brainy', 'Business', 'Car', 'Chance', 'Change', 'Christmas', 'Communication', 'Computers', 'Cool', 'Courage', 'Dad', 'Dating', 'Death', 'Design', 'Diet', 'Dreams', 'Easter', 'Education', 'Environmental', 'Equality', 'Experience', 'Failure', 'Faith', 'Family', 'Famous', 'Father\'s Day', 'Fear', 'Finance', 'Fitness', 'Food']
    # SCRAPE_OBJECT = ScrapeKeyword('Einstein', 30)
    START = time.time()
    # HTML_RESPONSE = SCRAPE_OBJECT.multi_scrape()
    # OBJECT = format_quotes(HTML_RESPONSE)
    # output_json(OBJECT)
    output_json(scrape_all(SCRAPE_LIST, 10))
    END = time.time()
    print('Time it takes to scrape: ', END - START, 'seconds')
