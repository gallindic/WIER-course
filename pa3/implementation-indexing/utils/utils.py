import os
from document import Document

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