from argparse import ArgumentParser
from regex_parser import regex_parse


SITES = {
    'overstock': [
        '../input-extraction/overstock.com/jewelry01.html',
        '../input-extraction/overstock.com/jewelry02.html'
    ],
    'rtvslo': [
        '../input-extraction/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html',
        '../input-extraction/rtvslo.si/Volvo XC 40 D4 AWD momentum_ suvereno med najboljše v razredu - RTVSLO.si.html'
    ]
}

def cmd_args():
    parser = ArgumentParser()
    
    parser.add_argument('--extraction', required=1, type=str, help='Extraction method used')
    parser.add_argument('--source', default='overstock', type=str, help='Input used for extraction')
    
    return parser.parse_args()


def get_html_code(page):
    htmlObject = open(page, 'rb')
    return htmlObject.read()


def run_regex(pages, source):
    for page in pages:
        regex_parse(get_html_code(page), source)


def run_extraction(args):
    pages = SITES[args.source]
    
    if args.extraction == 'A':
        run_regex(pages, args.source)
    elif args.extraction == 'B':
        pass
    elif args.extraction == 'C':
        pass
    else:
        print('Extraction method not found!')
    

if __name__ == '__main__':
    args = cmd_args()
    run_extraction(args)
    