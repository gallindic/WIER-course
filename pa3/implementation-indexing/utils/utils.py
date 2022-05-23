import os
from document import Document
from nltk import word_tokenize
from .stopwords import stop_words_slovene


def read_documents(documents_path):
    documents = []

    for domain in os.listdir(documents_path):
        domain_dir = os.path.join(documents_path, domain)

        for document in os.listdir(domain_dir):
            if '.html' not in document:
                continue

            #print(f'Processing {document}')
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

def get_prefix(url):
    if "e-prostor.gov.si" in url: prefix = "e-prostor.gov.si/"
    elif "e-uprava.gov.si" in url: prefix = "e-uprava.gov.si/"
    elif "evem.gov.si" in url: prefix = "evem.gov.si/"
    elif "podatki.gov.si" in url: prefix = "podatki.gov.si/"
    else: raise NotImplementedError

    return prefix + url