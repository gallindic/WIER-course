from crawler.crawler import Crawler
from crawler.manager import Manager
from crawler.frontier import init_frontier
from argparse import ArgumentParser

SEEDS = ['https://www.gov.si/', 'https://www.evem.gov.si/', 'https://www.e-uprava.gov.si/', 'https://www.e-prostor.gov.si/']
Seed_domains = ['https://www.gov.si', 'evem.gov.si', 'e-uprava.gov.si', 'e-prostor.gov.si']

def args():
    parser = ArgumentParser()

    parser.add_argument('--initFrontier', default=0, type=int, help='Initialized frontier with seed pages')
    parser.add_argument('--threads', default=1, type=int, help='Number of threads to run')

    return parser.parse_args()


def init_seeds():
    """
    Initializes frontier table in DB
    """
    for seed in SEEDS:
        init_frontier(seed)
    
    print("Frontier initialized")


def main(threads):
    crawler_threads = []

    manager = Manager(0)
    manager.start()

    for i in range(1, threads+1):
        crawler = Crawler(i)
        
        crawler.start()
        crawler_threads.append(crawler)

    manager.join()
    for crawler in crawler_threads:
        crawler.join()

    print("Finished crawling")


if __name__ == "__main__":
    arguments = args()

    if arguments.initFrontier:
        init_seeds()
        exit(0)
    
    main(arguments.threads)