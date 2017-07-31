"""
Multithreaded general purpose scraper for brainyquotes.com
"""
import sys
import threading
import time
from collections import defaultdict
from queue import Queue
import requests
from bs4 import BeautifulSoup, SoupStrainer
import keywords
import utils
import progressbar

class ScrapeKeyword(object):
    """docstring for ScrapeKeyword"""
    def __init__(self, keyword, num_pages):
        self.keyword = keyword
        self.num_pages = num_pages
        self.url = 'http://brainyquote.com/search_results.html?q={}'.format(keyword)
        self.lock = threading.Lock()

    def scrape_first_page(self, result):
        """Initializes scraping and gets first url page based on search word"""
        response = requests.get(self.url)
        parse_only = SoupStrainer(title=['view quote','view author'])
        soup = BeautifulSoup(response.content, 'lxml', parse_only=parse_only)
        result.append(soup) #soup.select('#quotesList a')
        #return result

    def multi_scrape_quotes(self, results, params):
        """Scrape brainyquotes based on search result multithreaded"""
        try:
            response = requests.post(self.url, params=params) # Get all search results
            parse_only = SoupStrainer(title=['view quote','view author'])
            soup = BeautifulSoup(response.content, 'lxml', parse_only=parse_only)
            #with self.lock:
            results.append(soup)#soup.select('#quotesList a')
        except requests.exceptions.RequestException:
            return

    def run_queue_page(self, que, soup):
        while True:
            param = que.get()
            if param is None:
                break
            self.multi_scrape_quotes(soup, param)
            que.task_done()

    def multi_scrape(self):
        """Multithreaded scrape implementation"""
        results = []
        self.scrape_first_page(results)
        parameters = ({"typ":"search", "langc":"en", "ab":"b", "pg":page, "id":self.keyword, "m":0} for page in range(self.num_pages))
        num_threads = 5
        pg_que = Queue()
        for param in parameters:
            pg_que.put(param)
        #threads = (threading.Thread(target=self.multi_scrape_quotes, args=(page, results, )) for page in range(2, self.num_pages + 1))
        for _ in range(num_threads):
            worker = threading.Thread(target=self.run_queue_page, args=(pg_que, results))
            worker.daemon = True
            worker.start()
            time.sleep(.01)
        pg_que.join()
        return results

def run_queue_author_quote(que, soup, page_range):
    """Scrape author and quote only"""
    while True:
        topic = que.get()
        if topic is None:
            break
        one_topic_obj = ScrapeKeyword(topic, page_range)
        soup.extend(one_topic_obj.multi_scrape())
        que.task_done()

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
        num_threads = 25 #optimal number of threads
    que = Queue()
    all_results = []
    for topic in scrape_list:
        que.put(topic)
    for _ in range(num_threads):
        worker = threading.Thread(target=run_queue_author_quote, args=(que, all_results, page_range))
        worker.daemon = True
        worker.start()
        time.sleep(.5)
        #progress(i, num_threads, status=' Scraping...')
    que.join()
    return format_quotes(all_results)

def format_quotes(quotes_list):
    """Format quotes to a dict"""
    quotes_list_result = []
    authors_list_result = []
    result = defaultdict(set)
    
    for quote in quotes_list:
        for q in quote.find_all(title='view quote'):
            quotes_list_result.append(q.text)
        for q in quote.find_all(title='view author'):
            authors_list_result.append(q.text)
        # new_quote = quote.find_all('a')
        # if new_quote.get('title') == 'view quote':
        #     quotes_list.append(new_quote.text)
        # if new_quote.get('title') == 'view author':
        #     authors_list.append(new_quote.text)
    for author, quote in zip(authors_list_result, quotes_list_result):
        result[author].add(quote)
    result = dict(result)
    for key, value in result.items():
        result[key] = list(value)
    return result

if __name__ == '__main__':
    ALL_TOPICS = keywords.ALL_TOPICS
    FILENAME = sys.argv[1]
    START = time.time()
    spinner = progressbar.Spinner()
    print('Scraping... ')
    spinner.start()
    utils.output_json(scrape_all(ALL_TOPICS, 20), FILENAME) if utils.validate_name(FILENAME) else sys.exit()
    END = time.time()
    spinner.stop()
    print('Done!')
    print('Time taken to scrape: {0:.2f} seconds'.format(END - START))
