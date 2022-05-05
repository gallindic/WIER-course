import re
import bs4
from lxml.html.clean import Cleaner


def runner(page1, page2):
    # print(page1, page2, source)
    out = ""

    pg1_content = open(page1, 'r', encoding="utf-8").read()
    pg2_content = open(page2, 'r', encoding="utf-8").read()

    pg1_cleaned = clean(pg1_content)
    pg2_cleaned = clean(pg2_content)

    pg1_tolist = listify(pg1_cleaned)
    pg2_tolist = listify(pg2_cleaned)

    regex_cmp = compare_pages(pg1_tolist, pg2_tolist)

    for ex in regex_cmp:
        out = out + ex + "\s*"

    out = str(out)
    out = re.sub("<(.*?[^/])>", "<\g<1>.*?>", out)
    out = re.sub("<(.*?)/>", "<\g<1>.*?/>", out)

    print(out)


def clean(page):
    cleaner = Cleaner(page_structure=False, style=True, safe_attrs=frozenset([]), )
    pg_clean = cleaner.clean_html(page)
    pg_clean = bs4.BeautifulSoup(pg_clean, "lxml").prettify()

    return pg_clean


def listify(page):
    pg_list = []

    while page:

        next_item, page = get_next_item(page)

        if next_item == "":
            continue

        else:
            pg_list.append(next_item)

    return pg_list


def get_next_item(page):
    idx = 0

    if page[idx] == "<":
        while page[idx] != ">":
            idx += 1

        return page[0:idx + 1].strip(), page[idx + 1:]

    else:
        while page[idx] != "<":
            idx += 1

        return re.escape(page[0:idx].strip()), page[idx:]


def compare_pages(page1, page2):
    comp = []
    i = 0
    j = 0

    while len(page1) > i and len(page2) > j:
        pg1_next = page1[i]
        pg2_next = page2[j]

        if pg1_next == pg2_next:
            comp.append(pg1_next)
            i = i + 1
            j = j + 1
            continue

        if check_tag(pg1_next):

            if check_tag(pg2_next):

                pg1_prev = get_previous_tag(page1, i)
                pg2_prev = get_previous_tag(page2, j)

                pg1_tag = get_tag(pg1_next)
                pg2_tag = get_tag(pg2_next)

                if check_tag(pg1_next, which_tag="start") and pg1_tag == pg1_prev:

                    isquare, index = iterator_square(pg1_prev, page1, i)
                    usquare = upper_square(page1, i)
                    it, it_reg = check_iterator(usquare, isquare)

                    if it:
                        comp = update_iterator_regex(comp, it_reg)
                        i = index + 1
                        continue

                if check_tag(pg2_next, which_tag="start") and pg2_tag == pg2_prev:

                    isquare, index = iterator_square(pg2_prev, page2, j)
                    usquare = upper_square(page2, j)
                    it, it_reg = check_iterator(usquare, isquare)

                    if it:
                        comp = update_iterator_regex(comp, it_reg)
                        j = index + 1
                        continue

                pg1_new, pg1_nexttag = get_next_tag(page1, i)
                pg2_new, pg2_nexttag = get_next_tag(page2, j)

                if not pg2_nexttag or pg1_nexttag == pg2_tag:

                    new_regex = page1[i:pg1_new]

                    if new_regex:
                        new_regex[0] = "(" + new_regex[0]
                        new_regex[-1] = new_regex[-1] + ")?"
                        comp = comp + new_regex

                    i = pg1_new

                if not pg1_nexttag or pg2_nexttag == pg1_tag:

                    new_regex = page2[j:pg2_new]

                    if new_regex:
                        new_regex[0] = "(" + new_regex[0]
                        new_regex[-1] = new_regex[-1] + ")?"
                        comp = comp + new_regex

                    j = pg2_new

                if pg2_nexttag != pg1_tag and pg1_nexttag != pg2_tag:

                    new_regex = page1[i:pg1_new]

                    if new_regex:
                        new_regex[0] = "(" + new_regex[0]
                        new_regex[-1] = new_regex[-1] + ")?"
                        comp = comp + new_regex

                    i = pg1_new

                    new_regex = page2[j:pg2_new]

                    if new_regex:
                        new_regex[0] = "(" + new_regex[0]
                        new_regex[-1] = new_regex[-1] + ")?"
                        comp = comp + new_regex

                    j = pg2_new

            else:
                comp.append("(.*?)")
                j = j + 1

        elif check_tag(pg2_next):
            comp.append("(.*?)")
            i = i + 1

        else:
            comp.append("(.*?)")
            i = i + 1
            j = j + 1

    return comp


def check_tag(input_str: str, which_tag='any'):
    test_tag = re.search("<(.*?)>", input_str)

    if which_tag == 'any':
        if test_tag:
            return True

        else:
            return None

    elif which_tag == 'start':
        if not test_tag:
            return None

        return not check_tag(input_str, 'both') and not check_tag(input_str, 'end')

    elif which_tag == 'both':
        if not test_tag:
            return None

        test = re.search("<([^/].*?/)>", input_str)

        if test:
            return True

        else:
            return False

    else:

        if not test_tag:
            return None

        test = re.search("<(/.*?[^/])>", input_str)

        if test:
            return True

        else:
            return False


def get_previous_tag(items_list, curr_idx):
    curr_idx = curr_idx - 1

    while not check_tag(items_list[curr_idx]):
        curr_idx -= 1

    tag = items_list[curr_idx]
    return "".join(filter(str.isalpha, tag))


def get_tag(input_str: str, get_all=False):
    tag_name = re.search("</?(\w*)?[\s\S]*>", input_str)

    if tag_name:
        tag_name = tag_name.group(1)

    if get_all:
        class_name = re.search("<[\s\S]*class=\"(.*?)\"[\s\S]*>", input_str)

        if class_name:
            class_name = class_name.group(1)

        tag_id = re.search("<[\s\S]*id=\"(.*?)\"[\s\S]*>", input_str)

        if tag_id:
            tag_id = tag_id.group(1)

        return tag_name, class_name, tag_id

    return tag_name


def iterator_square(tag_name, items_list, curr_idx):
    num_of_opening_tags = 1
    square_list = [items_list[curr_idx]]

    while num_of_opening_tags > 0 and curr_idx < len(items_list) - 1:

        curr_idx = curr_idx + 1
        next_item = items_list[curr_idx]
        tag = check_tag(next_item, which_tag="start")

        if tag is not None:
            if get_tag(next_item) == tag_name:

                if tag:
                    num_of_opening_tags += 1

                else:
                    num_of_opening_tags -= 1

        square_list.append(next_item)
    return square_list, curr_idx


def upper_square(items_list, curr_idx):
    num_of_closing_tags = 1
    idx = curr_idx - 1

    if not check_tag(items_list[idx], which_tag='end'):
        return []

    while num_of_closing_tags > 0:
        idx -= 1

        if idx < 0:
            return []

        if check_tag(items_list[idx], which_tag='end'):
            num_of_closing_tags += 1

        elif check_tag(items_list[idx], which_tag='start'):
            num_of_closing_tags -= 1

    return items_list[idx:curr_idx]


def check_iterator(wrapper_list, sample_list):
    if not wrapper_list or not sample_list:

        return False, None

    regex_list = []
    wrapper_idx = 0
    sample_idx = 0

    while wrapper_idx < len(wrapper_list) and sample_idx < len(sample_list):

        next_item_w = wrapper_list[wrapper_idx]
        next_item_s = sample_list[sample_idx]

        if next_item_w == next_item_s:

            regex_list.append(next_item_w)
            wrapper_idx += 1
            sample_idx += 1
            continue

        if check_tag(next_item_w):

            if check_tag(next_item_s):
                return False, None

            regex_list.append("(.*?)")
            sample_idx += 1

        elif check_tag(next_item_s):
            regex_list.append("(.*?)")
            wrapper_idx += 1

        else:
            regex_list.append("(.*?)")
            wrapper_idx += 1
            sample_idx += 1

    return True, regex_list


def update_iterator_regex(regex, iterator_regex):
    idx = len(regex) - 1
    iterator_tag_name = get_tag(iterator_regex[0])
    curr_tag_name = get_tag(regex[idx])

    if curr_tag_name != iterator_tag_name:
        num_of_closing_tags = 1

        while num_of_closing_tags > 0:
            idx -= 1

            if get_tag(regex[idx]) == curr_tag_name:

                tag_state = check_tag(regex[idx], which_tag="start")

                if tag_state:
                    num_of_closing_tags -= 1

                elif tag_state is False:
                    num_of_closing_tags += 1
        idx -= 1

        if get_tag(regex[idx]) != iterator_tag_name:
            print("Bad input regex!")
            return None

    end_idx = idx

    if regex[end_idx][-1] == "*":
        return regex

    num_of_closing_tags = 1

    while num_of_closing_tags > 0:

        idx -= 1

        if get_tag(regex[idx]) == iterator_tag_name:
            tag_state = check_tag(regex[idx], which_tag="start")

            if tag_state:
                num_of_closing_tags -= 1

            elif tag_state is False:
                num_of_closing_tags += 1

    start_idx = idx
    idx_diff = end_idx - start_idx + 1

    while start_idx - idx_diff >= 0:

        if regex[start_idx - idx_diff: start_idx] == iterator_regex:
            start_idx = start_idx - idx_diff

        else:
            break
    before_regex = regex[0:start_idx]

    if end_idx == len(regex) - 1:
        after_regex = []

    else:
        after_regex = regex[end_idx + 1:]

    iterator_regex[0] = "(" + iterator_regex[0]
    iterator_regex[-1] = iterator_regex[-1] + "\s*)*"

    return before_regex + iterator_regex + after_regex


def get_next_tag(html_list, index):
    if check_tag(html_list[index], which_tag='start'):
        # find tags end tag
        start_tags = 1
        while start_tags > 0:
            index += 1
            if index >= len(html_list):
                return index - 1, None
            is_start = check_tag(html_list[index], which_tag='start')
            if is_start:
                start_tags += 1
            elif is_start is False and not check_tag(html_list[index], which_tag='both'):
                start_tags -= 1

        while True:
            index += 1
            if index >= len(html_list):
                return index-1, None
            if check_tag(html_list[index]):
                return index, get_tag(html_list[index])

    return index, get_tag(html_list[index])