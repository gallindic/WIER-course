
def get_source_method(source):
    if source == 'overstock':
        return parse_overstock
    elif source == 'rtvslo':
        return parse_rtvslo
    

def parse_overstock(html_code):
    return html_code


def parse_rtvslo(html_code):
    return html_code


def regex_parse(html_code, source):
    method = get_source_method(source)
    print(method(html_code))