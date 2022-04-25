import json
import re


def get_source_method(source):
    if source == 'overstock':
        return parse_overstock
    elif source == 'rtvslo':
        return parse_rtvslo
    

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
    first = ' '.join(match.group(1).split())
    content = re.sub(r"<[^>]*>", "", first)

    return (
        json.dumps({
            "Author": author,
            "Date": date,
            "Title": title,
            "SubTitle": subtitle,
            "Abstract": abstract,
            "Content": content
        },
        ensure_ascii=False, indent=4)
    )


def regex_parse(html_code, source):
    method = get_source_method(source)
    print(method(html_code))