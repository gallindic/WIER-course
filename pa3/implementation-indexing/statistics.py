import sqlite3
from db.db import connect_to_db

conn = connect_to_db()

cursor = conn.cursor()

try:
    # query = 'SELECT COUNT(word) FROM IndexWord' # Count unique words in IndexWord
    # query = 'SELECT COUNT (word) FROM Posting' # Count unique postings in Posting
    # query = 'SELECT COUNT (DISTINCT documentName) FROM Posting' # Count all documents
    # query = 'SELECT word, COUNT(word) as c FROM Posting GROUP BY word ORDER BY c DESC LIMIT 30' # Count number of times words have appeared in all documents
    # query = 'Select word, frequency FROM Posting WHERE frequency >= 1000 ORDER BY frequency DESC' # Count most frequent words in a single document
    query = 'SELECT documentName, SUM(frequency) as freq FROM Posting GROUP BY documentName ORDER BY freq DESC LIMIT 5'
    cursor.execute(query)
    results = cursor.fetchall()
except Exception as e:
    print("Query failed: %s" % e)
    results = None

cursor.close()

print(results)