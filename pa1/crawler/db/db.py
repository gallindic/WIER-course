import threading
import configparser
from datetime import datetime
from string import Template

import psycopg2
from psycopg2 import pool, DatabaseError

config = configparser.ConfigParser()
config.read('db/db.ini')

try:
    thread_pool = pool.ThreadedConnectionPool(1, 64,
                                              database=config['postgresDB']['db'],
                                              user=config['postgresDB']['user'],
                                              password=config['postgresDB']['pass'],
                                              host=config['postgresDB']['host'],
                                              port=config['postgresDB']['port'])
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
    except Exception as e:
        print("Query failed:", e)
        id = None
    finally:
        thread_pool.putconn(conn)
        return id


def get_page_by_url(seed):
    try:
        conn = thread_pool.getconn()
        cur = conn.cursor()
        sql = "SELECT id FROM crawldb.page WHERE url=%s"
        cur.execute(sql, (seed,))
        id = cur.fetchone()
        cur.close()
        return id
    except Exception as e:
        print("Query failed:", e)
    finally:
        thread_pool.putconn(conn)


def get_page_by_canon_url(canon_seed):
    try:
        conn = thread_pool.getconn()
        cur = conn.cursor()
        sql = "SELECT id FROM crawldb.page WHERE canonUrl=%s"
        cur.execute(sql, (canon_seed,))
        id = cur.fetchone()
        cur.close()
    except Exception as e:
        print("Query failed:", e)
        id = None
    finally:
        thread_pool.putconn(conn)
        return id


def get_duplicate_page_id(canon_url):
    try:
        ps_connection = thread_pool.getconn()
        cur = ps_connection.cursor()
        sql = """SELECT id FROM crawldb.page WHERE url = %s AND page_type_code != 'DUPLICATE'"""
        cur.execute(sql, (canon_url,))
        id = cur.fetchone()[0]
        cur.close()
        thread_pool.putconn(ps_connection)
        print("Duplicate %s found" % canon_url)
        return id
    except (Exception, DatabaseError, pool.PoolError) as error:
        ps_connection.rollback()
        thread_pool.putconn(ps_connection)
        print(error)


def get_page_id_by_hash(hash):
    try:
        ps_connection = thread_pool.getconn()
        cur = ps_connection.cursor()
        sql = """SELECT id FROM crawldb.page WHERE hash = %s"""
        cur.execute(sql, (hash))
        id = cur.fetchone()[0]
        cur.close()
        thread_pool.putconn(ps_connection)
        print("Hash duplicate %s found" % hash)
        return id
    except (Exception, DatabaseError, pool.PoolError) as error:
        ps_connection.rollback()
        thread_pool.putconn(ps_connection)
        print(error)


def get_last_inserted(domain):
    try:
        conn = thread_pool.getconn()
        cur = conn.cursor()
        sql = Template("""SELECT id, url, accessed_time FROM crawldb.page WHERE page_type_code = 'HTML' and url LIKE '%%$domain%%' ORDER BY accessed_time DESC LIMIT 1""")
        cur.execute(sql.substitute(domain=domain))
        result = cur.fetchone()
        cur.close()
    except Exception as e:
        print("Query failed:", e)
        result = None
    finally:
        thread_pool.putconn(conn)
        return result


def getRobots(siteId):
    try:
        ps_connection = thread_pool.getconn()
        cur = ps_connection.cursor()
        sql = """SELECT robots_content FROM crawldb.site WHERE id=%s"""
        cur.execute(sql, (siteId,))
        data = cur.fetchone()[0]
        cur.close()
        thread_pool.putconn(ps_connection)
        return data

    except (Exception, psycopg2.DatabaseError, pool.PoolError) as error:
        ps_connection.rollback()
        thread_pool.putconn(ps_connection)
        print(error)


def insert_site(domain, robots_content, sitemap_content):
    try:
        conn = thread_pool.getconn()
        cur = conn.cursor()
        sql = "INSERT INTO crawldb.site (domain, robots_content, sitemap_content) VALUES (%s, %s, %s)"
        cur.execute(sql, (domain, robots_content, sitemap_content))
        conn.commit()
        print("Site %s inserted successfully" % domain)
    except Exception as e:
        print("Insertion failed:", e)
    finally:
        thread_pool.putconn(conn)


def insert_page(site_id, page_type_code, url, html_content=None, http_status_code=None, accessed_time=None, hash=None):
    try:
        conn = thread_pool.getconn()
        cur = conn.cursor()
        sql = "INSERT INTO crawldb.page (site_id, page_type_code, url, html_content, http_status_code, accessed_time, hash) VALUES (%s, %s, %s, %s, %s, %s, %s) returning id;"
        cur.execute(sql, (site_id, page_type_code, url, html_content, http_status_code, accessed_time, hash))
        conn.commit()
        page = cur.fetchone()
        print("Page %s inserted successfully" % url)
        return page
    except Exception as e:
        print("Insertion failed:", e)
    finally:
        thread_pool.putconn(conn)


def page_link_exists(from_page, to_page):
    try:
        conn = thread_pool.getconn()
        cur = conn.cursor()
        sql = "SELECT from_page FROM crawldb.link WHERE from_page=%s AND to_page=%s;"
        cur.execute(sql, (from_page, to_page))
        conn.commit()
        id = cur.fetchone()
        return id
    except Exception as e:
        print("Insertion failed:", e)
    finally:
        thread_pool.putconn(conn)


def insert_link(from_page, to_page):
    try:
        ps_connection = thread_pool.getconn()
        cur = ps_connection.cursor()
        sql = """INSERT INTO crawldb.link(from_page, to_page) VALUES(%s, %s);"""
        cur.execute(sql, (from_page, to_page))
        ps_connection.commit()
        thread_pool.putconn(ps_connection)
    except (Exception, DatabaseError, pool.PoolError) as error:
        ps_connection.rollback()
        thread_pool.putconn(ps_connection)
        print(error)


def update_frontier_entry(page_id, url, html_content, page_type_code, http_status_code, hash=None):
    try:
        conn = thread_pool.getconn()
        lock.acquire()
        cur = conn.cursor()
        sql = "UPDATE crawldb.page SET page_type_code=%s, html_content=%s, http_status_code=%s, accessed_time=%s, hash=%s where id=%s"
        cur.execute(sql, (page_type_code, html_content, http_status_code, datetime.now(), str(hash), page_id))
        conn.commit()
        lock.release()
        print("Page %s updated successfully" % url)
    except Exception as e:
        print("Insertion failed:", e)
    finally:
        thread_pool.putconn(conn)


def insert_binary(seedID, dataType, urlData):
    try:
        ps_connection = thread_pool.getconn()
        cur = ps_connection.cursor()
        # obtaing data_type_code from binary file
        sql = """select code from crawldb.data_type where code like %s"""
        cur.execute(sql, (dataType.split('.')[1].upper(),))
        extension = cur.fetchone()
        if extension is not None:
            sql = """INSERT INTO crawldb.page_data(page_id, data_type_code, data)
                                VALUES (%s, %s, %s);"""
            cur.execute(sql, (seedID, extension, None))
            ps_connection.commit()
        thread_pool.putconn(ps_connection)

    except (Exception, psycopg2.DatabaseError, pool.PoolError) as error:
        print(error)
        ps_connection.rollback()
        thread_pool.putconn(ps_connection)


def insert_image(seedID, imageName, imageContentType, imageBytes):
    try:
        ps_connection = thread_pool.getconn()
        cur = ps_connection.cursor()
        sql = """INSERT INTO crawldb.image(page_id, filename, content_type, accessed_time)
                             VALUES (%s,%s, %s, %s);"""
        cur.execute(sql, (seedID, imageName, imageContentType, datetime.now()))
        ps_connection.commit()
        thread_pool.putconn(ps_connection)

    except (Exception, psycopg2.DatabaseError, pool.PoolError) as error:
        print(error)
        ps_connection.rollback()
        thread_pool.putconn(ps_connection)


def get_next_seed():
    """
    Get next seed from frontier in DB
    """
    try:
        conn = thread_pool.getconn()
        lock.acquire()
        cur = conn.cursor()
        sql = """update crawldb.page set page_type_code=%s
                 where id=(SELECT p.id FROM crawldb.page p INNER JOIN crawldb.site s ON p.site_id = s.id
                    WHERE page_type_code=%s and s.domain NOT IN (SELECT DISTINCT domain FROM crawldb.scheduler)
                 ORDER BY id LIMIT 1)
                 returning id, url"""
        cur.execute(sql, (None, 'FRONTIER'))
        conn.commit()
        page = cur.fetchone()
        lock.release()
        thread_pool.putconn(conn)
        return page

    except (Exception, DatabaseError, pool.PoolError) as error:
        conn.rollback()
        lock.release()
        thread_pool.putconn(conn)
        print(error)


def insert_scheduler(domain=None, ip=None, delete_at=None):
    try:
        ps_connection = thread_pool.getconn()
        cur = ps_connection.cursor()
        sql = """INSERT INTO crawldb.scheduler(domain, ip, delete_at)
                             VALUES (%s,%s, %s);"""
        cur.execute(sql, (domain, ip, delete_at))
        ps_connection.commit()
        thread_pool.putconn(ps_connection)

    except (Exception, psycopg2.DatabaseError, pool.PoolError) as error:
        print(error)
        ps_connection.rollback()
        thread_pool.putconn(ps_connection)


def insert_site(domain, robots_content, sitemap_content):
    try:
        conn = thread_pool.getconn()
        cur = conn.cursor()
        sql = "INSERT INTO crawldb.site (domain, robots_content, sitemap_content) VALUES (%s, %s, %s)"
        cur.execute(sql, (domain, robots_content, sitemap_content))
        conn.commit()
        print("Site %s inserted successfully" % domain)
    except Exception as e:
        print("Insertion failed:", e)
    finally:
        thread_pool.putconn(conn)


def delete_from_scheduler():
    try:
        conn = thread_pool.getconn()
        lock.acquire()
        now = datetime.now()
        cur = conn.cursor()
        sql = "DELETE FROM crawldb.scheduler WHERE %s > delete_at"
        cur.execute(sql, (now,))
        conn.commit()
        lock.release()
    except Exception as e:
        print("Deletion failed:", e)
    finally:
        thread_pool.putconn(conn)


def get_frontier_len():
    try:
        conn = thread_pool.getconn()
        cur = conn.cursor()
        sql = "SELECT COUNT(id) FROM crawldb.page WHERE page_type_code='FRONTIER'"
        cur.execute(sql)
        count = cur.fetchone()[0]
        cur.close()
    except Exception as e:
        print("Query failed:", e)
        count = None
    finally:
        thread_pool.putconn(conn)
        return count


def get_pages_len():
    try:
        conn = thread_pool.getconn()
        cur = conn.cursor()
        sql = "SELECT COUNT(id) FROM crawldb.page"
        cur.execute(sql)
        count = cur.fetchone()[0]
        cur.close()
    except Exception as e:
        print("Query failed:", e)
        count = None
    finally:
        thread_pool.putconn(conn)
        return count