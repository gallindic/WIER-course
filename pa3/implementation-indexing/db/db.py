import sqlite3

DB_PATH = 'db/inverted-index.db'


def connect_to_db():
    return sqlite3.connect(DB_PATH)


def create_tables(conn):
    cursor = conn.cursor()

    with open('db/tables.sql', 'r') as sql_file:
        sql_script = sql_file.read()

        try:
            cursor.executescript(sql_script)
            conn.commit()
        except sqlite3.Error as err:
            print('Table creation error:', err)
            conn.close()
            exit(-1)
    
    print("Successfully created tables")
    cursor.close()


def clear_tables(conn):
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM IndexWord")
        cursor.execute("DELETE FROM Posting")

        conn.commit()
    except sqlite3.Error as err:
        print('Delete error:', err)
        conn.close()
        exit(-1)

    print("Successfully cleared tables")
    cursor.close()


def insert_posting(conn, document_name, postings):
    cursor = conn.cursor()

    for word, posting in postings.items():
        if len(posting['indexes']) > 1:
            indexes = ','.join([str(idx) for idx in posting['indexes']])
        else:
            indexes = str(posting['indexes'][0])

        try:
            cursor.execute("INSERT INTO IndexWord VALUES (?)", (word,))
        except sqlite3.IntegrityError:
            pass

        try:
            cursor.execute("INSERT INTO Posting VALUES (?, ?, ?, ?)", (word, document_name, posting["frequency"], indexes))
        except sqlite3.Error as err:
            print('Insert error:', err)
            conn.close()
            exit(-1)

        conn.commit()
        print(f"Inserted {word} from {document_name}")

    cursor.close()

def insert_document_text(conn, document_name, document_text):
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO DocumentText VALUES (?, ?)", (document_name, document_text))
    except sqlite3.Error as err:
        print('Insert error:', err)
        conn.close()
        exit(-1)

    conn.commit()
    print(f"Inserted text from {document_name}")

    cursor.close()

def get_query_words(conn, words_query):
    cursor = conn.cursor()

    try:
        search_query = "SELECT * FROM Posting WHERE word IN (" + "?, " * (len(words_query)-1) + "?)"
        cursor.execute(search_query, words_query)
        results = cursor.fetchall()
    except Exception as e:
        print("Query failed: %s" % e)
        results = None
    
    cursor.close()
    return results
    
def get_document_text(conn, site):
    cursor = conn.cursor()

    try:
        query = 'SELECT text FROM DocumentText WHERE documentName = ?'
        cursor.execute(query, (site,))
        results = cursor.fetchone()
    except Exception as e:
        print("Query failed: %s" % e)
        results = None
    
    cursor.close()
    return results