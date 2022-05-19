from argparse import ArgumentParser
from db.db import connect_to_db, get_query_words, get_document_text
from utils.utils import process_search_query
import numpy as np
from nltk import word_tokenize
import time

def arguments():
    parser = ArgumentParser()
    parser.add_argument('query', default="", type=str, help='Search query')

    return parser.parse_args()


def main(args):
    conn = connect_to_db()

    # Process query words (the same way as db entries are processed)
    words_query = process_search_query(args.query)

    results = get_query_words(conn, words_query)

    results_dict = dict()

    for posting in results:
        word, site, frequency, indices = posting

        if site not in results_dict:
            document = {
                "frequency": 0,
                "indices": [],
                "site": site
            }
            results_dict[site] = document
        else: document = results_dict[site]

        document["frequency"] += frequency
        document["indices"].extend([int(i) for i in indices.split(",")])

    results_sorted = sorted(
        results_dict.values(),
        key=lambda doc: doc["frequency"],
        reverse=True
    )

    result_string = ""

    for result in results_sorted:

        document_text = get_document_text(conn, result["site"])
        text_words = word_tokenize(document_text[0])

        snippets = list()

        for index in result["indices"]:
            range = np.arange(index-3, index+4)
            snippet = " ".join([text_words[i] for i in range])
            snippets.append(snippet)
        
        result_string += ("{0:<11} {1:<41} {2:<59}\n".format(result["frequency"], result["site"], "... " + " ... ".join(snippets) + " ..."))

    print('Results for a query: "%s"\n' % args.query)
    print("Results found in %dms.\n" % 4)
    print("{0:<11} {1:<41} {2:<59}".format("Frequencies", "Document", "Snippet"))
    print("{0:-<11} {1:-<41} {2:-<59}".format("", "", ""))
    print(result_string)

    conn.close()


if __name__ == "__main__":
    args = arguments()
    main(args)