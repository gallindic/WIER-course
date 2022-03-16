import psycopg2
import threading
from psycopg2 import pool

try:
    thread_pool = pool.ThreadedConnectionPool(1, 32,
                                                        database="postgres",
                                                        user="postgres",
                                                        password="root",
                                                        host="localhost",
                                                        port="5432")
    lock = threading.Lock()
    print("Connection established successfully")
except Exception as e:
    print("Connection failed:", e)

def get_site_id(domain):
    try:
        conn = thread_pool.getconn()
        cur = conn.cursor()
        sql = "SELECT id FROM crawldb.site WHERE domain=%s"
        cur.execute(sql, (domain,))
        id = cur.fetchone()
        cur.close()
        thread_pool.putconn(conn)
    except Exception as e:
        print("Query failed:", e)
        id = None
    finally:
        return id

def insert_site(domain, robots_content, sitemap_content):
    try:
        conn = thread_pool.getconn()
        cur = conn.cursor()
        sql = "INSERT INTO crawldb.site (domain, robots_content, sitemap_content) VALUES (%s, %s, %s)"
        cur.execute(sql, (domain, robots_content, sitemap_content))
        conn.commit()
        thread_pool.putconn(conn)
        print("Site %s inserted successfully" % domain)
    except Exception as e:
        print("Insertion failed:", e)

def insert_page(site_id, page_type_code, url, html_content=None, http_status_code=None, accessed_time=None):
    try:
        conn = thread_pool.getconn()
        cur = conn.cursor()
        sql = "INSERT INTO crawldb.page (site_id, page_type_code, url, html_content, http_status_code, accessed_time) VALUES (%s, %s, %s, %s, %s, %s)"
        cur.execute(sql, (site_id, page_type_code, url, html_content, http_status_code, accessed_time))
        conn.commit()
        thread_pool.putconn(conn)
        print("Page %s inserted successfully" % url)
    except Exception as e:
        print("Insertion failed:", e)


def get_next_seed():
    """
    Get next seed from frontier in DB
    """
    raise NotImplementedError()
