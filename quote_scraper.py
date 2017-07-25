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
    SCRAPE_ALL_TOPICS = ['Age', 'Alone', 'Amazing', 'Anger', 'Anniversary', 'Architecture', 'Art', 'Attitude', 'Beauty', 'Best', 'Birthday', 'Brainy', 'Business', 'Car', 'Chance', 'Change', 'Christmas', 'Communication', 'Computers', 'Cool', 'Courage', 'Dad', 'Dating', 'Death', 'Design', 'Diet', 'Dreams', 'Easter', 'Education', 'Environmental', 'Equality', 'Experience', 'Failure', 'Faith', 'Family', 'Famous', 'Father\'s Day', 'Fear', 'Finance', 'Fitness', 'Food', 'Forgiveness', 'Freedome', 'Friendship', 'Funny', 'Future', 'Gardening', 'God', 'Good', 'Government', 'Graduation', 'Great', 'Happiness', 'Health', 'History', 'Home', 'Hope', 'Humor', 'Imagination', 'Independence', 'Inspirational', 'Intelligence', 'Jealousy', 'Knowledge', 'Leadership', 'Learning', 'Legal', 'Life', 'Love', 'Marriage', 'Medical', 'Memorial Day', 'Men', 'Mom', 'Money', 'Morning', 'Mother\'s Day', 'Motivational', 'Movies', 'Moving On', 'Music', 'Nature', 'New Year\'s', 'Parenting', 'Patience', 'Patriotism', 'Peace', 'Pet', 'Poetry', 'Politics', 'Positive', 'Power', 'Relationship', 'Religion', 'Respect', 'Romantic', 'Sad', 'Saint Patrick\'s Day', 'Science', 'Smile', 'Society', 'Space', 'Sports', 'Strength', 'Success', 'Sympathy', 'Teacher', 'Technology', 'Teen', 'Thankful', 'Thanksgiving', 'Time', 'Travel', 'Trust', 'Truth', 'Valentine\'s Day', 'Veterans Day', 'War', 'Wedding', 'Wisdom', 'Women', 'Work']
    FILENAME = sys.argv[1]
    START = time.time()
    output_json(scrape_all(SCRAPE_ALL_TOPICS, 10), FILENAME) if validate_name(FILENAME) else sys.exit()
    END = time.time()
    print('Time taken to scrape: {0:.2f} seconds'.format(END - START))
