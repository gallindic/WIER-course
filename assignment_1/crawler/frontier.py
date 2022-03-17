from os import dup
from urllib.parse import urlparse
import requests
import re
from db.db import get_site_id, insert_site, insert_page, get_page_by_canon_url, insert_link, get_duplicate_page_id, get_page_by_url, page_link_exists

DOMAINS = ['www.gov.si', 'www.evem.gov.si', 'www.e-uprava.gov.si', 'www.e-prostor.gov.si']

def process_robots(path):
    try:
        response = requests.get(path)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except:
        return None


def process_sitemap(text):
    match = re.search(r"Sitemap:\s*([^\s\n\r]*)", text)
    if match is None: return None
    sitemap = requests.get(match.group(1))
    return sitemap.text


def init_frontier(seed):
    print("Processing", seed)

    url_parsed = urlparse(seed)
    domain = url_parsed.netloc
    
    robots = process_robots(seed + "robots.txt")
    sitemap = process_sitemap(robots) if robots is not None else None

    insert_site(domain, robots, sitemap)
    site_id = get_site_id(domain)

    insert_page(site_id, "FRONTIER", seed)


def process_frontier(seed, domain, current_page_id):
    if domain not in DOMAINS:
        return

    url_parsed = urlparse(seed)
    seedCanonicalization = url_parsed.netloc + url_parsed.path
    seedCanonicalization = seedCanonicalization + '?' + url_parsed.query if url_parsed.query != "" else seedCanonicalization
    seedCanonicalization = seedCanonicalization[:-1] if seedCanonicalization.endswith('/') else seedCanonicalization
    
    if url_parsed.scheme and url_parsed.scheme not in seedCanonicalization:
        seedCanonicalization = url_parsed.scheme + '://' + seedCanonicalization
    elif 'http' not in seedCanonicalization:
        seedCanonicalization = 'http://' + seedCanonicalization

    duplicate_page_id = get_page_by_url(seedCanonicalization)

    if duplicate_page_id is not None:
        if not page_link_exists(current_page_id, duplicate_page_id[0]):
            insert_link(current_page_id, duplicate_page_id[0])
        
        return

    site_id = get_site_id(domain)
    next_page_id = insert_page(site_id, 'FRONTIER', seedCanonicalization, html_content=None)
    
    if not page_link_exists(current_page_id, next_page_id[0]):
        insert_link(current_page_id, next_page_id[0])
        