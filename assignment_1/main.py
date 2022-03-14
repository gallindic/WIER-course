from crawler.crawler import Crawler
from argparse import ArgumentParser

seeds = ['http://www.mgrt.gov.si/','http://www.mz.gov.si/',
            'http://www.uvps.gov.si/','http://www.mju.gov.si/',
            'http://www.osha.mddsz.gov.si/']

def args():
    parser = ArgumentParser()

    parser.add_argument('--initFrontier', default=0, type=int, help='Initialized frontier with seed pages')
    parser.add_argument('--threads', default=8, type=int, help='Number of threads to run')

    return parser.parse_args()


def init_frontier():
    """
    Initializes frontier table in DB
    """
    for seed in seeds:
        #Saves seed to pages table in DB
        pass
    
    print("Frontier initialized")


def main(threads):
    crawler_threads = []

    for i in range(threads):
        crawler = Crawler(i)
        
        crawler.start()
        crawler_threads.append(crawler)

    for crawler in crawler_threads:
        crawler.join()

    print("Finished crawling")


if __name__ == "__main__":
    arguments = args()

    if arguments.initFrontier:
        init_frontier()
        exit(0)
    
    main(arguments.threads)