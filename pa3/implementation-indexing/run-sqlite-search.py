from argparse import ArgumentParser
from db.db import connect_to_db, get_query_words, get_document_text
from utils.utils import process_search_query
import numpy as np
from nltk import word_tokenize
import datetime

def arguments():
    parser = ArgumentParser()
    parser.add_argument('query', default="", type=str, help='Search query')

    return parser.parse_args()


def main(args):
    conn = connect_to_db()

    start_time = datetime.datetime.now()

    # Process query words (the same way as db entries are processed)
    words_query = process_search_query(args.query)

    # Get all postings that contain query words
    results = get_query_words(conn, words_query)

    # Count frequencies of words
    results_dict = dict()
    for posting in results:
        word, site, frequency, indexes = posting

        if site not in results_dict:
            document = {
                "frequency": 0,
                "indexes": [],
                "site": site
            }
            results_dict[site] = document
        else: document = results_dict[site]

        document["frequency"] += frequency
        document["indexes"].extend([int(i) for i in indexes.split(",")])

    # Sort the results by frequencies
    results_sorted = sorted(
        results_dict.values(),
        key=lambda doc: (doc["frequency"], doc["site"]),
        reverse=True
    )

    # Construct snippets
    result_string = ""
    for result in results_sorted:

        document_text = get_document_text(conn, result["site"])
        text_words = word_tokenize(document_text[0])

        snippets = list()

        for index in result["indexes"]:
            range = np.arange(index-3, index+4)
            snippet = " ".join([text_words[i] for i in range])
            snippets.append(snippet)
        
        result_string += ("{0:<11} {1:<41} {2:<59}\n".format(result["frequency"], result["site"], "... " + " ... ".join(snippets) + " ..."))

    end_time = datetime.datetime.now()
    delta = end_time - start_time

    print('Results for a query: "%s"\n' % args.query)
    print("Results found in %dms.\n" % int(delta.total_seconds() * 1000))
    print("{0:<11} {1:<41} {2:<59}".format("Frequencies", "Document", "Snippet"))
    print("{0:-<11} {1:-<41} {2:-<59}".format("", "", ""))
    print(result_string)

    """file = open('test.txt','w', encoding="utf8")
    file.write('Results for a query: "%s"\n\n' % args.query)
    file.write("Results found in %dms.\n\n" % int(delta.total_seconds() * 1000))
    file.write("{0:<11} {1:<41} {2:<59}\n".format("Frequencies", "Document", "Snippet"))
    file.write("{0:-<11} {1:-<41} {2:-<59}\n".format("", "", ""))
    file.write(result_string)"""

    conn.close()


if __name__ == "__main__":
    args = arguments()
    main(args)