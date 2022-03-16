from urllib.parse import urlparse
import requests
import re
from db.db import get_site_id, insert_site, insert_page

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

def process_frontier(seed):
    print("Processing", seed)

    url_parsed = urlparse(seed)
    domain = url_parsed.netloc
    
    robots = process_robots(seed + "robots.txt")
    sitemap = process_sitemap(robots) if robots is not None else None

    site_id = get_site_id(domain)
    if site_id is None: insert_site(domain, robots, sitemap)

    insert_page(site_id, "FRONTIER", seed)