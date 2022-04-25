from lxml.html.soupparser import fromstring
from lxml.etree import tostring
import json
import re


def get_source_method(source):
    if source == 'overstock':
        return parse_overstock
    elif source == 'rtvslo':
        return parse_rtvslo
    elif source == 'bolha':
        return parse_bolha
    

def parse_overstock(html_code):
    root_element = fromstring(html_code)
    #print(tostring(root_element))

    products = root_element.xpath("/html//body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr")
    prdcts = []

    for product in products:
        if len(product.text_content()) == 0: continue

        # Title - Overstock
        title = product.xpath("./td[2]/a/b")
        if len(title) == 0: continue
        title = title[0].text_content()
        
        # LastPrices - Overstock
        list_price = product.xpath("./td[2]/table/tbody/tr[1]/td[1]/table/tbody/tr[1]/td[2]/s")[0].text_content()
        
        # Prices - Overstock
        price = product.xpath("./td[2]/table/tbody/tr[1]/td[1]/table/tbody/tr[2]/td[2]/span")[0].text_content()

        # Savings and SavingPercents - Overstock
        savings, savings_percents = product.xpath("./td[2]/table/tbody/tr[1]/td[1]/table/tbody/tr[3]/td[2]/span")[0].text_content().split()

        # Content - Overstock
        content = product.xpath("./td[2]/table/tbody/tr[1]/td[2]/span")[0].text_content()
        content = ' '.join(content.split()) # TODO: how to filter content?

        prdcts.append({
            "ListPrice": list_price,
            "Price": price,
            "Saving": savings,
            "SavingPercent": savings_percents,
            "Title": title,
            "Content": content
        })

    return json.dumps([dump for dump in prdcts], indent=4)
    


def parse_rtvslo(html_code):
    root_element = fromstring(html_code)
    
    # Author - RTV
    author = root_element.xpath("//div[@class='author-name']")[0].text_content()

    # Title - RTV
    title = root_element.xpath("//h1")[0].text_content()

    # Subtitle - RTV
    subtitle = root_element.xpath("//div[@class='subtitle']")[0].text_content()

    # Date - RTV
    date = root_element.xpath("//div[@class='publish-meta']")[0].text_content()
    date = re.sub(r"[^a-zA-Z0-9 .:]", "", date.splitlines()[1])

    # Lead - RTV
    abstract = root_element.xpath("//p[@class='lead']")[0].text_content()

    # Content - RTV
    content = root_element.xpath("//article[@class='article']")[0].text_content()
    content = ' '.join(content.split()) # TODO: how to filter content?

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
    root_element = fromstring(html_code)

    # Title - Bolha
    title = root_element.xpath("//h1[@class='entity-title']")[0].text_content()

    # Price - Bolha
    price = root_element.xpath("//li[@class='price-item price-item--base']/strong")[0].text_content()
    price = ' '.join(price.split())
    
    # Id - Bolha
    id = root_element.xpath("//b[@class='base-entity-id']")[0].text_content()

    # PublishedTime - Bolha
    published_time = root_element.xpath("//li[@class='meta-item meta-item--hidden']/time")[0].text_content()
    
    # ValidUntil - Bolha
    valid_until = root_element.xpath("//li[@class='meta-item meta-item--hidden']/span/span[@class='base-entity-display-expires-on']")[0].text_content()
    
    # Views - Bolha
    views = root_element.xpath("//li[@class='meta-item meta-item--hidden']/span/span[@class='base-entity-display-count']")[0].text_content()
    
    table_summary = root_element.xpath("//table[@class='table-summary table-summary--alpha']/tbody")[0]

    # Type - Bolha
    type = table_summary.xpath("./tr[1]/td")[0].text_content()

    # Location - Bolha
    location = table_summary.xpath("./tr[2]/td")[0].text_content()

    # Status - Bolha
    status = table_summary.xpath("./tr[3]/td")[0].text_content()
    
    # Content - Bolha
    content = root_element.xpath("//div[@class='passage-standard passage-standard--alpha']/div/p")[0].text_content()
    content = ' '.join(content.split()) # TODO: how to filter content?
    
    return (
        json.dumps({
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
        },
        ensure_ascii=False, indent=4)
    )


def xpath_parse(html_code, source):
    method = get_source_method(source)
    print(method(html_code))