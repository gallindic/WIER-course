from argparse import ArgumentParser
from regex_parser import regex_parse
from xpath_parser import xpath_parse
import codecs
from lxml.html.clean import Cleaner
from roadrunner import runner


SITES = {
    'overstock': [
        '../input-extraction/overstock.com/jewelry01.html',
        '../input-extraction/overstock.com/jewelry02.html'
    ],
    'rtvslo': [
        '../input-extraction/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html',
        '../input-extraction/rtvslo.si/Volvo XC 40 D4 AWD momentum_ suvereno med najboljše v razredu - RTVSLO.si.html'
    ],
    'bolha': [
        '../input-extraction/bolha.com/advertisement01.html',
        '../input-extraction/bolha.com/advertisement02.html'
    ]
}

cleaner = Cleaner()

def cmd_args():
    parser = ArgumentParser()
    
    parser.add_argument('--extraction', required=1, type=str, help='Extraction method used')
    parser.add_argument('--source', default='overstock', type=str, help='Input used for extraction')
    
    return parser.parse_args()


def get_html_code(page):
    page = codecs.open(page, encoding='utf-8', errors='replace').read()
    return cleaner.clean_html(page)


def run_regex(pages, source):    
    for page in pages:
        regex_parse(get_html_code(page), source)


def run_xpath(pages, source):    
    for page in pages:
        xpath_parse(get_html_code(page), source)


def run_runner(pages, source):
    runner(pages[0], pages[1])


def run_extraction(args):
    pages = SITES[args.source]
    
    if args.extraction == 'A':
        run_regex(pages, args.source)
    elif args.extraction == 'B':
        run_xpath(pages, args.source)
    elif args.extraction == 'C':
        run_runner(pages, args.source)
    else:
        print('Extraction method not found!')
    

if __name__ == '__main__':
    args = cmd_args()
    run_extraction(args)