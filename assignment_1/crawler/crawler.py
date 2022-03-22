import hashlib
import requests
import hashlib
import threading
from selenium import webdriver
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from .frontier import process_frontier
from assignment_1.db.db import get_next_seed, update_frontier_entry, get_page_id_by_hash, insert_link
import time


class Crawler(threading.Thread):
    def __init__(self, thread_id):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.user_agent = "fri-wier-course-group"
        self.driver = self._init_webdriver()

    def _init_webdriver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--user-agent=%s' % self.user_agent)
        options.add_argument('--disable-browser-side-navigation')
        options.headless = True
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(chrome_options=options)
        driver.set_page_load_timeout(20)
        driver.implicitly_wait(3)

        return driver


    def process_link(self, link, url, page_id):
        url_scheme = urlparse(url)

        if 'http' not in link:
            if not link.startswith('/') and not link.startswith('#'):
                link = url_scheme.scheme + '://' + url_scheme.netloc + '/' + link
            else:
                link = url_scheme.scheme + '://' + url_scheme.netloc + link
        
        process_frontier(link, urlparse(link).netloc, page_id)


    def parse_html(self, url, html_content, page_id):
        soup = BeautifulSoup(html_content, 'html.parser')

        for s in soup(['script', 'style']):
            s.decompose()

        for link in soup.find_all('a', href=True):
            new_link = str(link.get('href'))
            self.process_link(new_link, url, page_id)


    def crawl_page(self, page_id, response):
        # Wait 5 seconds between crawling
        time.sleep(5)
        print("Waiting 5 seconds")

        self.driver.get(response.url)

        html_content = self.driver.page_source
        is_html = 'html' in html_content
        page_type_code = 'HTML' if is_html else 'BINARY'

        if is_html:
            html_hash = hashlib.md5(html_content.encode()).hexdigest()

            duplicate_page_id = get_page_id_by_hash(html_hash)
            if duplicate_page_id:
                print("duplicate")
                insert_link(page_id, duplicate_page_id)
                page_type_code = 'DUPLICATE'
                html_content = None

            update_frontier_entry(page_id, response.url, html_content, page_type_code, response.status_code, hash=html_hash)
            self.parse_html(response.url, html_content, page_id)
        else:
            #save binaries
            pass


    def run(self):
        next_page = get_next_seed()

        while next_page is not None:
            page_id, url = next_page

            url = url.replace('www.', '')
            response = requests.get(url)
            
            self.crawl_page(page_id, response)

            next_page = get_next_seed()

        print(f"Crawler {self.thread_id} finished crawling")
        self.driver.quit()