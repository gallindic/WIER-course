from utils.utils import read_documents, process_search_query, get_prefix
import datetime
from argparse import ArgumentParser
import numpy as np



def arguments():
    parser = ArgumentParser()
    parser.add_argument('query', default="", type=str, help='Search query')

    return parser.parse_args()


def main(args):
    start_time = datetime.datetime.now()
    results_dict = dict()

    # Process query words (the same way as db entries are processed)
    words_query = process_search_query(args.query)

    # Read all documents and create a Document object for each document
    documents = read_documents('../data/')

    for doc in documents:
        frequency = 0
        indexes = list()
        # If document contains word
        for word in sorted(words_query):
            if word in doc.postings.keys():
                frequency += doc.postings[word]["frequency"]
                indexes.extend(doc.postings[word]["indexes"])

        # If query words are in document
        if frequency > 0:
            document = {
                "frequency": frequency,
                "indexes": indexes,
                "site": doc.name,
                "text": doc.get_text_words()
            }
            results_dict[doc.name] = document

    # Sort the results by frequencies
    results_sorted = sorted(
        results_dict.values(),
        key=lambda doc: (doc["frequency"], doc["site"]),
        reverse=True
    )

    # Construct snippets
    result_string = ""
    for result in results_sorted:

        text_words = result["text"]

        snippets = list()

        for index in result["indexes"]:
            range = np.arange(index - 3, index + 4)
            snippet = " ".join([text_words[i] for i in range])
            snippets.append(snippet)

        result_string += ("{0:<11} {1:<41} {2:<59}\n".format(result["frequency"], get_prefix(result["site"]), "... " + " ... ".join(snippets) + " ..."))

    end_time = datetime.datetime.now()
    delta = end_time - start_time

    print('Results for a query: "%s"\n' % args.query)
    print("Results found in %dms.\n" % int(delta.total_seconds() * 1000))
    print("{0:<11} {1:<41} {2:<59}".format("Frequencies", "Document", "Snippet"))
    print("{0:-<11} {1:-<41} {2:-<59}".format("", "", ""))
    print(result_string)


if __name__ == "__main__":
    args = arguments()
    main(args)