from cgitb import text
from bs4 import BeautifulSoup
from nltk import word_tokenize
from utils.stopwords import stop_words_slovene

class Document:
    def __init__(self, name, document_path):
        self.name = name
        self.path = document_path
        self.postings = self._process_document()

    
    def _process_document(self):
        with open(self.path, "r", encoding="utf8") as doc:
            soup = BeautifulSoup(doc.read(), "html.parser")

            for data in soup(['style', 'script']):
                data.decompose()

            postings = {}
            text_words = word_tokenize(soup.get_text())

            for idx, word in enumerate(text_words):
                word_data = word.lower()

                if word_data in stop_words_slovene:
                    continue

                if word_data in postings:
                    data = postings[word_data]

                    data['frequency'] += 1
                    data['indexes'].append(idx)

                    postings[word_data] = data
                else:
                    postings[word_data] = {
                        "frequency": 1, 
                        "indexes": [idx]
                    }
            
            return postings


    def get_postings(self):
        return self.postings


    def get_name(self):
        return self.name