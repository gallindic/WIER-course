import os
from configparser import ConfigParser

import psycopg2
import json

conn = None

try:

    dump = {}
    dump['nodes'] = []
    dump['links'] = []

    conn = psycopg2.connect(
        host="localhost",
        port="5433",
        database="postgres",
        user="postgres",
        password="root")

    cur = conn.cursor()

    print('\n')
    cur.execute("SELECT * FROM crawldb.page WHERE page_type_code = 'HTML' AND page.url LIKE '%e-uprava.gov.si/podrocja/drzava-druzba%'")
    whole = cur.fetchall()

    for row in whole:
        dump['nodes'].append({
            'id': str(row[0]),
            'group': 131,
            'url': str(row[3]),
            'type': 'HTML'
        })

        l = str(row[0])

        cur.execute("SELECT * FROM crawldb.link \n" +
                    "WHERE from_page = %s", (l,))
        links = cur.fetchall()
        for link in links:
            if link[1] != row[0]:
                dump['links'].append({
                    'source': link[0],
                    'target': link[1],
                    'value' : 1
                })

    cur.close()

    badids = []
    goodids = []

    for link in dump['links']:
        count = 0
        for node in dump['nodes']:
            if str(link['source']) == node['id']:
                for an_node in dump['nodes']:
                    if str(link['target']) == an_node['id']:
                        count = count + 1
        if count == 0:
            print('removing ' + str(link['target']))
            badids.append(link)
        else:
            print('adding ' + str(link['target']))
            goodids.append(link)

    dump['links'] = goodids

    with open('e-prostor_web.json', 'w') as outfile:
        json.dump(dump, outfile, indent=4)

except (Exception, psycopg2.DatabaseError) as error:
    print(error)
finally:
    if conn is not None:
        conn.close()
        print('Database connection closed.')