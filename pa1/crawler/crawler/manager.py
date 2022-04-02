import threading
from db.db import delete_from_scheduler, get_frontier_len, get_pages_len
import time

class Manager(threading.Thread):
    def __init__(self, thread_id):
        threading.Thread.__init__(self)
        self.thread_id = thread_id

    def run(self):
        while True:
            delete_from_scheduler()
            time.sleep(0.5)