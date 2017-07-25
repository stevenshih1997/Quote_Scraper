#!/usr/bin/env python3
import json
import threading
import time
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
#from queue import Queue
#lock = threading.Lock()
class scrape_topic(object):
    """docstring for scrape_topic"""
    def __init__(self):
        super(scrape_topic, self).__init__()

        
# def scrape_quotes(search_result):
#     """Scrape brainyquotes based on search result"""
#     num_pages = 5
#     url = 'http://brainyquote.com/search_results.html?q={}'.format(search_result)
#     all_response = requests.get(url) # Get first page search result
#     soup = BeautifulSoup(all_response.content, 'html.parser')
#     all_quotes = soup.select('#quotesList a')
#     for pages in range(2, num_pages + 1):
#         parameters = {"typ":"search", "langc":"en", "ab":"b", "pg":pages, "id":search_result, "m":0}
#         response = requests.post(url, params=parameters) # Get all search results
#         soup = BeautifulSoup(response.content, 'html.parser')
#         all_quotes += soup.select('#quotesList a')
#     return all_quotes

def first_scrape(search_result):
    url = 'http://brainyquote.com/search_results.html?q={}'.format(search_result)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')
    quotes = soup.select('#quotesList a')
    return (quotes, url)

def multi_scrape_quotes(search_result, url, page_number, results):
    """Scrape brainyquotes based on search result multithreaded"""
    #url = first_scrape(search_result)[1]
   # url = 'http://brainyquote.com/search_results.html?q={}'.format(search_result)
    #all_response = requests.get(url) # Get first page search result
    #soup = BeautifulSoup(all_response.content, 'html.parser')
    #all_quotes = soup.select('#quotesList a')
    parameters = {"typ":"search", "langc":"en", "ab":"b", "pg":page_number, "id":search_result, "m":0}
    response = requests.post(url, params=parameters) # Get all search results
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'lxml')
    #results.put(soup.select('#quotesList a'))
    #with lock:
    results += soup.select('#quotesList a')
    #results.append(soup.select('#quotesList a'))

def multi_scrape(pages, keyword):
    url_result_tuple = first_scrape(keyword)
    results = url_result_tuple[0]
    url = url_result_tuple[1]
    threads = [threading.Thread(target=multi_scrape_quotes, args=(keyword, url, i, results)) for i in range(2, pages + 1)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    #que.join()
    return results

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
    #return dict(zip(authors_list, quotes_list))
    result = dict(result)
    for key, value in result.items():
        result[key] = list(value)
    return dict(result)

def output_json(input_quotes):
    json.dump(input_quotes, open('./quotes.json', 'w'), indent=4, sort_keys=True)

if __name__ == '__main__':
    # START = time.time()
    # QUOTES = scrape_quotes('inspirational')
    # print(format_quotes(QUOTES))
    # END = time.time()
    # print(END - START)
    START = time.time()    
    #print(format_quotes(scrape_quotes('inspirational')))
    HTML_RESPONSE = multi_scrape(20, 'Love')
    END = time.time()
    OBJECT = format_quotes(HTML_RESPONSE)
    print(type(OBJECT['Ram Dass']))
    #SEQUENTIAL_RES = scrape_quotes('inspirational')
    #MULTI_RES = multi_scrape(5)
    output_json(OBJECT)
    print(END - START)
    
