from urllib.parse import urlparse
import requests
import re

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
    
    robots = process_robots(seed + "robots.txt")
    sitemap = process_sitemap(robots) if robots is not None else None

    print(robots)
    print(sitemap[:100])
