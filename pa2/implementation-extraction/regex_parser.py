import json
import re
from xml import etree

def get_source_method(source):
    if source == 'overstock':
        return parse_overstock
    elif source == 'rtvslo':
        return parse_rtvslo
    elif source == 'bolha':
        return parse_bolha
    

def parse_overstock(html_code):
    prodId = 0
    prdcts = []

    # Title - Overstock
    regex = r"<b>([0-9]+-(.+)(?=\</b>))</b>"
    titles = []
    matches = re.finditer(regex, html_code)
    for match in matches:
        titles.append(match.group(1))

    # LastPrices - Overstock
    regex = r"<s>(.*?)</s>"
    listPrices = []
    matches = re.finditer(regex, html_code)
    for match in matches:
        listPrices.append(match.group(1))

    # Prices - Overstock
    regex = r"<b>([$€]\s*[0-9\.,]+)</b>"
    prices = []
    matches = re.finditer(regex, html_code)
    for match in matches:
        prices.append(match.group(1))

    # Content - OverStock
    regex = r"<td valign=\"top\"><span class=\"normal\">(.*?)<\/b>"
    contents = []
    matches = re.finditer(regex, html_code, re.DOTALL)
    for match in matches:
        content = ' '.join(match.group(1).split())
        final = re.sub(r"<[^>]*>", "", content)
        contents.append(final)

    # Percents - Overstock
    regex = r"\(([0-9]+%\))"
    percents = []
    matches = re.finditer(regex, html_code)
    for match in matches:
        percents.append(match.group(0))

    # Savings - Overstock
    regex = r"([$€]\s*[0-9\.,]+ )"
    savings = []
    matches = re.finditer(regex, html_code)
    for match in matches:
        savings.append(match.group(1).strip())

    while len(titles) > prodId:
        prdcts.append({
            "ListPrice": listPrices[prodId],
            "Price": prices[prodId],
            "Saving": savings[prodId],
            "SavingPercent": percents[prodId],
            "Title": titles[prodId],
            "Content": contents[prodId]
        })

        prodId = prodId + 1

    return json.dumps([dump for dump in prdcts], indent=4)


def parse_rtvslo(html_code):
    # Author - RTV
    regex = r"<div class=\"author-name\">(.*)</div>"
    match = re.compile(regex).search(html_code)
    author = match.group(1)

    # Title - RTV
    regex = r"<h1>(.*)<\/h1>"
    match = re.compile(regex).search(html_code)
    title = match.group(1)

    # Subtitle - RTV
    regex = r"<div class=\"subtitle\">(.*)</div>"
    match = re.compile(regex).search(html_code)
    subtitle = match.group(1)

    # Date - RTV
    regex = r"<div class=\"publish-meta\">(.*?)<br>"
    match = re.search(regex, html_code, re.DOTALL)
    date = match.group(1)
    date = ' '.join(date.split())

    # Lead - RTV
    regex = r"<p class=\"lead\">(.*)</p>"
    match = re.compile(regex).search(html_code)
    abstract = match.group(1)

    # Content - RTV
    regex = r"<article class=\"article\">(.*?)<\/article>"
    match = re.search(regex, html_code, re.DOTALL)
    content = ' '.join(match.group(1).split())
    content = re.sub(r'<[^>]+>', "", content)
    content = re.sub(' +', ' ', content).strip()

    return (
        json.dumps({
            "Author": author,
            "PublishedTime": date,
            "Title": title,
            "SubTitle": subtitle,
            "Lead": abstract,
            "Content": content
        },
        ensure_ascii=False, indent=4)
    )


def parse_bolha(html_code):
    # Title - Bolha
    regex = r"<h1 class=\"entity-title\">(.*)<\/h1>"
    match = re.compile(regex).search(html_code)
    title = match.group(1)

    # Price - Bolha
    regex = r"<strong class=\"price price--hrk\">(.*?)<\/strong>"
    match = re.search(regex, html_code, re.DOTALL)
    price = match.group(1)
    price = ' '.join(match.group(1).split())
    price = re.sub(r'<[^>]+>', "", price)
    price = re.sub(' +', ' ', price).strip()

    # Id - Bolha
    regex = r"<b class=\"base-entity-id\">(.*)<\/b>"
    match = re.compile(regex).search(html_code)
    id = match.group(1)

    # PubishedTIme - Bolha
    regex = r"<time class=\"value\" \s*.*>(.*)<\/time>"
    match = re.compile(regex).search(html_code)
    published_time = match.group(1)

    # ValidUntil - Bolha
    regex = r"<span class=\"base-entity-display-expires-on\">(.*)<\/span>"
    match = re.compile(regex).search(html_code)
    valid_until = match.group(1)
    valid_until = re.sub(' +', ' ', valid_until).strip()

    # Views - Bolha
    regex = r"<span class=\"base-entity-display-count\">(.*)<\/span>"
    match = re.compile(regex).search(html_code)
    views = match.group(1)
    views = ' '.join(match.group(1).split())
    views = re.sub(r'<[^>]+>', "", views).split()[0]

    # Table/table body 
    regex = r"<table class=\"table-summary table-summary--alpha\" cellpadding=\"0\" cellspacing=\"0\">(.*?)<\/table>"
    match = re.search(regex, html_code, re.DOTALL)
    table = match.group(1)
    table = re.sub(' +', ' ', table).strip()

    regex = r"<tbody>(.*?)<\/tbody>"
    match = re.search(regex, table, re.DOTALL)
    table_body = match.group(1)
    table_body = re.sub(' +', ' ', table_body).strip()

    # Type - Bolha
    regex = r"<td>(.*?)<\/td>"
    match = re.findall(regex, table_body, re.DOTALL)
    type = match[0]

    # Location - Bolha
    location = match[1]

    # Status - Bolha
    status = match[2]

    # Content - Bolha
    regex = r"<div id=\"base-entity-description-wrapper\">(.*?)<\/div>"
    match = re.search(regex, html_code, re.DOTALL)
    container = match.group(1)
    container = re.sub(' +', '', container).strip()

    regex = r"<p>(.*?)<\/p>"
    match = re.search(regex, html_code, re.DOTALL)
    content = match.group(1)
    content = re.sub(r'<[^>]+>', "", content)
    content = re.sub(r'\n', " ", content)
    content = re.sub(' +', ' ', content).strip()

    return json.dumps({
        "Title": title,
        "Price": price,
        "Id": id,
        "PublishedTime": published_time,
        "ValidUntil": valid_until,
        "Views": views,
        "Type": type,
        "Location": location,
        "Status": status,
        "Content": content
    }, ensure_ascii=False, indent=4)               


def regex_parse(html_code, source):
    method = get_source_method(source)
    print(method(html_code))