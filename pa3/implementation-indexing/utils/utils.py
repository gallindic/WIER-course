import os
from document import Document
from nltk import word_tokenize
from .stopwords import stop_words_slovene


DOCUMENTS_PATH = '../data/'


def read_documents():
    documents = []

    for domain in os.listdir(DOCUMENTS_PATH):
        domain_dir = os.path.join(DOCUMENTS_PATH, domain)

        for document in os.listdir(domain_dir):
            if '.html' not in document:
                continue

            print(f'Processing {document}')
            documents.append(Document(document, os.path.join(domain_dir, document)))

    return documents

def process_search_query(query):
    text_words = word_tokenize(query)

    query_words = list()

    for _, word in enumerate(text_words):
        word = word.lower()

        if word in stop_words_slovene:
            continue

        if word not in query_words:
            query_words.append(word)
    
    return query_words