import os
from document import Document
from argparse import ArgumentParser
from db.db import connect_to_db, create_tables, clear_tables, insert_into_db
from utils.utils import read_documents


def arguments():
    parser = ArgumentParser()
    parser.add_argument('--init_tables', default=0, type=int, help='Initialize database tables')
    parser.add_argument('--clear_tables', default=0, type=int, help='Clear database tables data')

    return parser.parse_args()


def main(args):
    conn = connect_to_db()

    if args.init_tables:
        create_tables(conn)

    if args.clear_tables:
        clear_tables(conn)

    documents = read_documents()

    print(len(documents))

    for doc in documents:
        insert_into_db(conn, doc.get_name(), doc.get_postings())

    conn.close()


if __name__ == "__main__":
    args = arguments()
    main(args)