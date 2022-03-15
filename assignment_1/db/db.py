import psycopg2

def get_next_seed():
    """
    Get next seed from frontier in DB
    """
    raise NotImplementedError()


conn = psycopg2.connect(
    dbname = "postgres",
    user = "postgres",
    host = "localhost", # Change host to IPAddress of pg_container
    password = "root"
)

cursor = conn.cursor()

cursor.close()

conn.close()
