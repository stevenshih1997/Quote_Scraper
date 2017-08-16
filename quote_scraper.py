"""
Multithreaded general purpose scraper for brainyquotes.com.
Ensure that there is a stable connection before attempting to scrape.
"""
import threading
import time
from collections import defaultdict
from queue import Queue
from bs4 import BeautifulSoup, SoupStrainer
import requests
from requests.adapters import HTTPAdapter
# Specify number of threads to scrape each page, and each topic
NUM_THREADS = (5, 25)

class ScrapeKeyword(object):
    """Scraper object which scrapes one keyword"""
    def __init__(self, keyword, num_pages):
        self.keyword = keyword
        self.num_pages = num_pages
        self.url = 'http://brainyquote.com/search_results.html?q={}'.format(keyword)

    def scrape_first_page(self, result, session):
        """Initializes scraping and gets first url page based on search word"""
        try:
            response = session.get(self.url)
            parse_only = SoupStrainer(title=['view quote', 'view author'])
            soup = BeautifulSoup(response.content, 'lxml', parse_only=parse_only)
            result.append(soup)
        except requests.exceptions.RequestException:
            return

    def multi_scrape_quotes(self, results, params, session):
        """Scrapes a page of a keyword previously specified"""
        try:
            response = session.post(self.url, params=params) # Get all search results
            parse_only = SoupStrainer(title=['view quote', 'view author'])
            soup = BeautifulSoup(response.content, 'lxml', parse_only=parse_only)
            results.append(soup)
        except requests.exceptions.RequestException as err:
            print(err)
            return

    def run_queue_page(self, que, soup, session):
        """ Multithreaded queue to scrape keyword"""
        while True:
            param = que.get()
            # breaks out of main thread so threads can join
            if param is None:
                break
            self.multi_scrape_quotes(soup, param, session)
            que.task_done()

    def multi_scrape(self, session):
        """Multithreaded scrape implementation; uses queue to manage threads"""
        results = []
        num_threads = NUM_THREADS[0]
        self.scrape_first_page(results, session)
        # parameters for post request is a generator
        parameters = ({"typ":"search", "langc":"en", "ab":"b", "pg":page, "id":self.keyword, "m":0} for page in range(self.num_pages))
        pg_que = Queue()
        for param in parameters:
            pg_que.put(param)
        for _ in range(num_threads):
            worker = threading.Thread(target=self.run_queue_page, args=(pg_que, results, session))
            worker.daemon = True
            worker.start()
            time.sleep(.1)
        pg_que.join()
        return results
    
    @staticmethod
    def run_queue_author_quote(que, soup, page_range, session):
        """Option to scrape author and quote only; has queue to manage threads"""
        while True:
            topic = que.get()
            # breaks out of main thread so threads can join
            if topic is None:
                break
            one_topic_obj = ScrapeKeyword(topic, page_range)
            soup.extend(one_topic_obj.multi_scrape(session))
            que.task_done()
    
    @staticmethod
    def run_queue(que, all_dict, page_range, session):
        """Option to organize in terms of keywords; has queue to manage threads"""
        while True:
            topic = que.get()
            # breaks out of main thread so threads can join
            if topic is None:
                break
            one_topic_obj = ScrapeKeyword(topic, page_range)
            all_dict[topic] = ScrapeKeyword.format_quotes(one_topic_obj.multi_scrape(session))
            que.task_done()
    
    @staticmethod
    def scrape_all(scrape_list, page_range, flag_topic):
        """
        Scrape all contents passed in @param scrape_list, specified in keywords.py
        """
        session = requests.Session()
        session.mount('http://', HTTPAdapter(max_retries=8))
        if len(scrape_list) < 20:
            num_threads = len(scrape_list)
        else:
            num_threads = NUM_THREADS[1] #optimal number of threads
        que = Queue()
        for topic in scrape_list:
            que.put(topic)
        # if flag true: allows organizing by keywords. Else, simply scrape author:quote
        if flag_topic:
            all_results = {}
            for _ in range(num_threads):
                worker = threading.Thread(target=ScrapeKeyword.run_queue, args=(que, all_results, page_range, session))
                worker.daemon = True
                worker.start()
                time.sleep(.5)
        else:
            all_results = []
            for _ in range(num_threads):
                worker = threading.Thread(target=ScrapeKeyword.run_queue_author_quote, args=(que, all_results, page_range, session))
                worker.daemon = True
                worker.start()
                time.sleep(.5)
        que.join()
        if flag_topic:
            return all_results
        return ScrapeKeyword.format_quotes(all_results)

    @staticmethod
    def format_quotes(quotes_list):
        """Format quotes to output in a json file"""
        quotes_list_result = []
        authors_list_result = []
        result = defaultdict(set)
        for quote in quotes_list:
            for quote_tag in quote.find_all(title='view quote'):
                quotes_list_result.append(quote_tag.text)
            for quote_tag in quote.find_all(title='view author'):
                authors_list_result.append(quote_tag.text)
        for author, quote in zip(authors_list_result, quotes_list_result):
            result[author].add(quote)
        result = dict(result)
        for key, value in result.items():
            result[key] = list(value)
        return result
