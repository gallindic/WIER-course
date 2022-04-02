import hashlib
import io
import urllib

import requests
import hashlib
import threading
import wget
import os
from selenium import webdriver
from PIL import Image
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from .frontier import process_frontier, process_robots, process_sitemap
from db.db import get_next_seed, get_site_id, insert_scheduler, insert_site, update_frontier_entry, get_page_id_by_hash, insert_link,\
    insert_image, insert_binary
import time
import datetime

binaryFiles = ['.pdf', '.doc', '.ppt', '.docx', '.pptx']
saveBinaries = 1
saveImages = 1
cur = os.getcwd()


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

        for imageTag in soup.find_all('img'):
            src = str(imageTag.get('src'))

            if 'http' not in src:
                urlParsed = urlparse(url)
                src = urlParsed.scheme + '://' + urlParsed.netloc + src

            self.process_image(src, page_id)

        for link in soup.find_all('a', href=True):
            new_link = str(link.get('href'))
            self.process_link(new_link, url, page_id)


    def __del__(self):
        self.driver.quit()


    def parse_onclick(self, page_id):
        for onclick in self.driver.find_elements_by_xpath('//*[@onclick]'):
            try:
                onclick.click()
                window_handles = self.driver.window_handles

                if len(window_handles) > 1:
                    self.driver.switch_to.window(window_handles[1])

                process_frontier(self.driver.current_url, urlparse(self.driver.current_url).netloc, page_id)

                if len(window_handles) == 1:
                    self.driver.back()
                else:
                    for window in window_handles[1:]:
                        self.driver.switch_to.window(window)
                        self.driver.close()
                    self.driver.switch_to.window(window_handles[0])
            except Exception as err:
                print(err)


    def crawl_page(self, page_id, response):
        try:
            domain = urlparse(response.url).netloc
            if "gov.si" not in domain: return

            # Insert new domain into Site
            if get_site_id(domain) is None:
                robots = process_robots(response.url + "robots.txt")
                sitemap = process_sitemap(robots) if robots is not None else None
                insert_site(domain, robots, sitemap)

            self.driver.get(response.url)
        except Exception as err:
            print(err)
            return

        html_content = self.driver.page_source
        is_html = 'text/html' in response.headers['content-type']

        if is_html:
            page_type_code = 'HTML'
            html_hash = hashlib.md5(html_content.encode()).hexdigest()

            self.parse_onclick(page_id)

            duplicate_page_id = get_page_id_by_hash(html_hash)
            if duplicate_page_id:
                print("duplicate")
                insert_link(page_id, duplicate_page_id)
                page_type_code = 'DUPLICATE'
                html_content = None

            update_frontier_entry(page_id, response.url, html_content, page_type_code, response.status_code,
                                  hash=html_hash)
            self.parse_html(response.url, html_content, page_id)
        else:
            page_type_code = 'BINARY'
            urlData = response.url
            
            update_frontier_entry(page_id, response.url, None, page_type_code, response.status_code)

            for suffix in binaryFiles:
                if suffix in urlData:
                    try:
                        insert_binary(page_id, suffix, response)

                        if saveBinaries == 1:
                            break
                        

                        if saveBinaries == 0:
                            if not os.path.exists(str(page_id)):
                                os.mkdir(str(page_id))
                            wget.download(response.url, out=str(str(page_id) + '\\'))
                    except Exception as error:
                        print(error)
            

    def process_image(self, url, page_id):
        try:
            urlParts = urllib.parse.urlparse(url)
            name = urlParts[2].rpartition('/')[2]

            type = 'unknown'

            imageRequest = requests.get(url, stream=True).raw
            imageObject = Image.open(imageRequest)

            imageBytes = io.BytesIO()

            if '.jpg' in url or '.jpeg' in url:
                imageObject.save(imageBytes, format='JPEG')
                type = 'JPG' if '.jpeg' in url else 'JPEG'

            elif '.png' in url:
                imageObject.save(imageBytes, format='PNG')
                type = 'PNG'

            elif '.gif' in url:
                imageObject.save(imageBytes, format='GIF')
                type = 'GIF'

            elif '.tiff' in url:
                imageObject.save(imageBytes, format='TIFF')
                type = 'TIFF'

            elif '.webp' in url:
                imageObject.save(imageBytes, format='WEBP')
                type = 'WEBP'

            elif '.bmp' in url:
                imageObject.save(imageBytes, format='BMP')
                type = 'BMP'

            else:
                imageObject.save(imageBytes)

            if saveImages == 1:
                imageBytes = None

            if saveImages == 0:
                if not os.path.exists(str(page_id)):
                    os.mkdir(str(page_id))
                wget.download(url, out=str(str(page_id) + '\\'))

            insert_image(page_id, name, type, imageBytes)

        except (Exception, IOError) as error:
            print(error)


    def run(self):
        next_page = get_next_seed()

        if next_page is None:
            time.sleep(10)
            next_page = get_next_seed()


        while next_page is not None:
            page_id, url = next_page

            try:
                domain = urlparse(url).netloc
                insert_scheduler(domain, None, datetime.datetime.now() + datetime.timedelta(seconds=5))
               
                url = url.replace('www.', '')
                response = requests.get(url)
                
                self.crawl_page(page_id, response)
            except requests.exceptions.HTTPError as errh:
                print ("Http Error:",errh)
            except requests.exceptions.ConnectionError as errc:
                print ("Error Connecting:",errc)
            except requests.exceptions.Timeout as errt:
                print ("Timeout Error:",errt)
            except requests.exceptions.RequestException as err:
                print ("OOps: Something Else",err)


            next_page = get_next_seed()

            if next_page is None:
                time.sleep(2)
                next_page = get_next_seed()
            
        print(f"Crawler {self.thread_id} finished crawling")