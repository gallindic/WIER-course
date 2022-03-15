import threading
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from db.db import get_next_seed


class Crawler(threading.Thread):
    def __init__(self, thread_id):
        threading.Thread.__init__(self)
        self.thread_id = thread_id


    def crawl_page(self, page):
        raise NotImplementedError()


    def run(self):
        next_page = get_next_seed()

        while next_page is not None:
            print("Crawling page x")
            self.crawl_page(next_page)
            
            next_page = get_next_seed()