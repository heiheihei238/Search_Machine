import time
import re
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver


def handle_http_requests(url):
    driver = webdriver.Chrome()
    driver.get(url)  # 写上自己的链接
    time.sleep(0.5)
    content = driver.page_source
    driver.close()
    return content


def get_related_articles(articles, keyword):
    """
    The articles are already found according to start time and end time.
    This function further filters out articles that meet the relevance criteria.
    :param articles: Information on all articles within the specified date range
    :param keyword: user defined keyword
    :return: results: dict
    """
    results = {}
    for i, t in articles.items():
        if is_related(t['url'], keyword):
            results.update({i: t})
    return results


def is_related(url, keyword):
    """
    to judge if an article meets the relevance criteria
    :param url: the url of the article
    :param keyword: user defined keyword
    :return: True or False
    """
    html = handle_http_requests(url)
    distance = find_min_distance_between_regex_matches(html, keyword)
    print(f'the distance is {distance} in {url}')
    return True if distance < 2000 else False


def find_min_distance_between_regex_matches(html, keyword):
    """
    regex1: the regex of t-test
    :param html: html content
    :param keyword: the keyword string given by the user
    :return: if no match is found, return -1. Otherwise returns the minimum distance
    """
    # Find all matches for the first regular expression
    regex1 = re.compile(r'\b(<\w+>)*t(</\w+>)*[\s-]*tests?\b', re.IGNORECASE)
    regex2 = re.compile(rf'{regex_keyword(keyword)}', re.IGNORECASE)

    matches1 = list(re.finditer(regex1, html))
    if not matches1:
        print("First match not found")
        return float('inf')

    # Find all matches for the second regular expression
    matches2 = list(re.finditer(regex2, html))
    if not matches2:
        print("Second match not found")
        return float('inf')

    # Calculate the distance between each pair of matched items and return the minimum value
    min_distance = float('inf')  # positive infinity
    for match1 in matches1:
        for match2 in matches2:
            distance = abs(match2.start() - match1.end())
            if distance < min_distance:
                min_distance = distance

    if min_distance == float('inf'):
        print("No matches found")
        return float('inf')

    return min_distance


def regex_keyword(string, regex=re.compile(r'\b[A-Za-z]\b', re.IGNORECASE)):
    """
    Allow individual letters to be wrapped in html tags in the keywords entered by the user
    :param string: the user-defined keyword
    :param regex:
    :return: the wrapped string
    """
    pattern = re.compile(regex)
    matches = pattern.finditer(string)
    indices = [match.span() for match in matches]
    indices = [(idx[0], idx[1]) for idx in indices]

    new_string = ""
    last_index = 0
    for index in indices:
        new_string += string[last_index:index[0]] + "(<\\w+>)*" + string[index[0]:index[1]] + "(</\\w+>)*"
        last_index = index[1]
    new_string += string[last_index:]
    result_string = new_string.replace(" ", "[\\s]*")
    result_string = '\\b' + result_string + 's?\\b'

    # \b(<\w+>)*n(</\w+>)*[\s]*=[\s]*3\b
    return result_string


def get_articles_by_date_range(start_time, end_time, keyword, classification):
    """
    All articles with "t-test" and the keyword inputted by user within the specified date range
    will be found in this method
    :param classification:
    :param url: the first page of pagination. The default value belong to global search
    :param start_time: '01 January 2010'
    :param end_time: '01 February 2012'
    :param keyword: 'p-value'
    :return: articles:dict
    {'BMP8A sustains spermatogenesis by activating both SMAD1/5/8 and SMAD2/3 in spermatogonia':
        {'title': 'BMP8A sustains spermatogenesis by activating both SMAD1/5/8 and SMAD2/3 in spermatogonia',
         'url': 'https://www.science.org/doi/10.1126/scisignal.aal1910',
         'pdf': 'https://www.science.org/doi/pdf/10.1126/scisignal.aal1910?download=true',
         'authors': 'by Fang-Ju Wu, Ting-Yu Lin, Li-Ying Sung, Wei-Fang Chang, Po-Chih Wu, Ching-Wei Luo',
         'published_time': '02 May 2017'},
     'Arabidopsis ATXR2 deposits H3K36me3 at the promoters of LBD genes to facilitate cellular dedifferentiation':
        {'title': 'Arabidopsis ATXR2 deposits H3K36me3 at the promoters of LBD genes to facilitate cellular dedifferentiation',
         'url': 'https://www.science.org/doi/10.1126/scisignal.aan0316',
         'pdf': 'https://www.science.org/doi/pdf/10.1126/scisignal.aan0316?download=true',
         'authors': 'by Kyounghee Lee, Ok-Sun Park, Pil Joon Seo',
         'published_time': '28 Nov 2017'}, ...
    }
    """
    results = {}
    last_article = binary_search_for_article(start_time, keyword, False, classification)
    first_article = binary_search_for_article(end_time, keyword, True, classification)
    first_page = int(first_article['page'])
    last_page = int(last_article['page'])
    end_date = datetime.strptime(convert_date_format2(end_time, '%d %B %Y'), '%d %B %Y')
    start_date = datetime.strptime(convert_date_format2(start_time, '%d %B %Y'), '%d %B %Y')

    # get valid articles in the first and the last page
    # Get the articles according to a date range in a page
    if classification == 12:  # global search
        url1 = f'https://journals.plos.org/plosbiology/search?unformattedQuery=(' \
               f'everything%3At-test)%20AND%20everything%3A{keyword}&q=(everything%3At-test)%20AND%20everyth' \
               f'ing%3A{keyword}&sortOrder=DATE_NEWEST_FIRST&page={first_page}&utm_content=a&utm_campaign=ENG-467'
        url2 = f'https://journals.plos.org/plosbiology/search?unformattedQuery=(' \
               f'everything%3At-test)%20AND%20everything%3A{keyword}&q=(everything%3At-test)%20AND%20everyth' \
               f'ing%3A{keyword}&sortOrder=DATE_NEWEST_FIRST&page={last_page}&utm_content=a&utm_campaign=ENG-467'
    else:  # classification search
        classifi = find_classification(classification)
        url1 = f'https://journals.plos.org/plosbiology/search?filterJournals={classifi}&unformattedQuery=(' \
               f'everything%3At-test)%20AND%20everything%3A{keyword}&q=(everything%3At-test)%20AND%20everyth' \
               f'ing%3A{keyword}&sortOrder=DATE_NEWEST_FIRST&page={first_page}&utm_content=a&utm_campaign=ENG-467'
        url2 = f'https://journals.plos.org/plosbiology/search?filterJournals={classifi}&unformattedQuery=(' \
               f'everything%3At-test)%20AND%20everything%3A{keyword}&q=(everything%3At-test)%20AND%20everyth' \
               f'ing%3A{keyword}&sortOrder=DATE_NEWEST_FIRST&page={last_page}&utm_content=a&utm_campaign=ENG-467'
    x1 = get_all_articles(url1)
    x2 = get_all_articles(url2)
    merged_articles = {**x1, **x2}
    for i, t in merged_articles.items():
        date = datetime.strptime(t["published_time"], '%d %B %Y')
        if start_date <= date <= end_date:
            results.update({i: t})

    # get articles exclude the first and the last page
    page_list = [i for i in range(first_page + 1, int(last_page))]
    if classification == 12:  # global search
        url_list = [
            f'https://journals.plos.org/plosbiology/search?unformattedQuery=(everything%3At-test)%20AND%20everything%3A{keyword}&q=(everything%3At-test)%20AND%20everything%3A{keyword}&sortOrder=DATE_NEWEST_FIRST&page={page}&utm_content=a&utm_campaign=ENG-467'
            for page in page_list]
    else:  # classification search
        classifi = find_classification(classification)
        url_list = [
            f'https://journals.plos.org/plosbiology/search?filterJournals={classifi}&unformattedQuery=(everything%3At-test)%20AND%20everything%3A{keyword}&q=(everything%3At-test)%20AND%20everything%3A{keyword}&sortOrder=DATE_NEWEST_FIRST&page={page}&utm_content=a&utm_campaign=ENG-467'
            for page in page_list]
    for url in url_list:
        articles = get_all_articles(url)
        results.update(articles)
    return results


def find_classification(classification_num):
    classification = ""
    match classification_num:
        case 0:
            classification = "PLoSBiology"
        case 1:
            classification = "PLOSClimate"
        case 2:
            classification = "PLoSCompBiol"
        case 3:
            classification = "PLOSDigitalHealth"
        case 4:
            classification = "PLoSGenetics"
        case 5:
            classification = "PLOSGlobalPublicHealth"
        case 6:
            classification = "PLoSMedicine"
        case 7:
            classification = "PLoSNTD"
        case 8:
            classification = "PLoSONE"
        case 9:
            classification = "PLoSPathogens"
        case 10:
            classification = "PLOSSustainabilityTransformation"
        case 11:
            classification = "PLOSWater"
    return classification


def convert_date_format1(input_date_str, output_format):
    # 将输入的日期字符串解析为日期对象
    input_date = datetime.strptime(input_date_str, '%d-%b-%Y')
    # 使用 strftime 方法将日期对象格式化为目标格式
    output_date_str = input_date.strftime(output_format)
    return output_date_str


def convert_date_format2(input_date_str, output_format):
    # 将输入的日期字符串解析为日期对象
    input_date = datetime.strptime(input_date_str, '%m/%d/%Y')
    # 使用 strftime 方法将日期对象格式化为目标格式
    output_date_str = input_date.strftime(output_format)
    return output_date_str


def binary_search_for_article(date, keyword, tag, classification):
    """
    Search for an article according to the specified date and on which page it appears
    :param classification:
    :param url:
    :param tag: if False ==> Looking for the last article published on or before that date
                if True ==> Looking for the first article published on or after that date
    :param date: '01 January 2010'
    :param keyword: 'p-value'
    :return: article: {'page': 3, 'article': {'title': 'Debaryomyces hansenii supplementation in low fish meal diets
                       promotes growth, modulates microbiota and enhances intestinal condition in juvenile marine fish',
                       'published_time': '9 July 2023', 'url':
                       'https://www.biomedcentral.com/search//jasbsci.biomedcentral.com/10.1186/s40104-023-00895-4',
                       'authors': 'Ignasi Sanahuja, Alberto Ruiz, Joana P. Firmino, Felipe E. Reyes-López,
                       Juan B. Ortiz-Delgado, Eva Vallejos-Vidal, Lluis Tort, Dariel Tovar-Ramírez, Isabel M. Cerezo,
                       Miguel A. Moriñigo, Carmen Sarasquete and Enric Gisbert'}}

    """
    # user specified date
    d = datetime.strptime(convert_date_format2(date, '%d %B %Y'), '%d %B %Y')
    # get the number of total page
    if classification == 12:  # global search
        url = f'https://journals.plos.org/plosbiology/search?unformattedQuery=(' \
              f'everything%3At-test)%20AND%20everything%3A{keyword}&q=(everything%3At-test)%20AND%20everyth' \
              f'ing%3A{keyword}&sortOrder=DATE_NEWEST_FIRST&page=1&utm_content=a&utm_campaign=ENG-467'
    else:  # classification search
        classifi = find_classification(classification)
        url = f'https://journals.plos.org/plosbiology/search?filterJournals={classifi}&unformattedQuery=(' \
              f'everything%3At-test)%20AND%20everything%3A{keyword}&q=(everything%3At-test)%20AND%20everyth' \
              f'ing%3A{keyword}&sortOrder=DATE_NEWEST_FIRST&page=1&utm_content=a&utm_campaign=ENG-467'
    html = handle_http_requests(url)
    soup = BeautifulSoup(html, 'html.parser')
    page_a = soup.find_all(attrs={"class": "number seq text-color"})
    pages = [int(p.get_text()) for p in page_a]
    if len(pages) == 0:  # there are only one page in the search results pagination
        page = 1
    else:
        page = pages[-1]
    article = {}

    # binary search
    low = 0
    high = int(page)
    current_page = high // 2
    tag1 = 0  # in order to handle particular situation
    while low <= high:
        print(current_page)
        if classification == 12:  # global search
            url = f'https://journals.plos.org/plosbiology/search?unformattedQuery=(' \
                  f'everything%3At-test)%20AND%20everything%3A{keyword}&q=(' \
                  f'everything%3At-test)%20AND%20everything%3A{keyword}&sortOrder=DATE_NEWEST_FIRST&page=' \
                  f'{current_page}&utm_content=a&utm_campaign=ENG-467'
        else:  # classification search
            classifi = find_classification(classification)
            url = f'https://journals.plos.org/plosbiology/search?filterJournals={classifi}&unformattedQuery=(' \
                  f'everything%3At-test)%20AND%20everything%3A{keyword}&q=(' \
                  f'everything%3At-test)%20AND%20everything%3A{keyword}&sortOrder=DATE_NEWEST_FIRST&page=' \
                  f'{current_page}&utm_content=a&utm_campaign=ENG-467'
        html = handle_http_requests(url)
        soup = BeautifulSoup(html, 'html.parser')
        # find the published date of the first article in one page
        times = []
        for n in range(0, 15):
            result = soup.find(attrs={"id": "article-result-" + str(n) + "-date"})
            if result:
                result = result.get_text(strip=True).replace("published ", '').replace(' ', '-')
                times.append(result)
            else:
                break
        # the published date of the first article in one page
        d1 = datetime.strptime(convert_date_format1(times[0], '%d %B %Y'), '%d %B %Y')
        # the published date of the last article in one page
        d2 = datetime.strptime(convert_date_format1(times[-1], '%d %B %Y'), '%d %B %Y')
        if current_page == page or current_page == 1:
            break
        if d == d1 == d2:
            if tag:
                tag1 = 2
                current_page -= 1
            else:
                tag1 = 1
                current_page += 1
        elif d == d1 > d2:
            if tag:
                tag1 = 2
                current_page -= 1
            else:
                break
        elif d > d1 >= d2:
            # the particular situation: for example:
            # the last article of page 50: 07 Juli; the last article of page 51: 06 Juli;
            # target date: 07 Juli; tag: False
            if tag1 == 1:
                current_page -= 1
                break
            else:
                high = current_page - 1
                current_page = (low + high) // 2

        elif d1 > d > d2:
            break
        elif d1 > d2 == d:
            if tag:
                break
            else:
                tag1 = 1
                current_page += 1
        elif d1 >= d2 > d:
            # the particular situation: for example:
            # the last article of page 50: 07 Juli; the first article of page 51: 06 Juli;
            # target date: 06 Juli; tag: True
            if tag1 == 2:
                current_page += 1
                break
            else:
                low = current_page + 1
                current_page = (low + high) // 2
        else:
            print("error occurred in binary search")
            break

    # get url
    if classification == 12:  # global search
        url = f'https://journals.plos.org/plosbiology/search?unformattedQuery=(' \
              f'everything%3At-test)%20AND%20everything%3A{keyword}&q=(everything%3At-test)%20AND%20everyth' \
              f'ing%3A{keyword}&sortOrder=DATE_NEWEST_FIRST&page={current_page}&utm_content=a&utm_campaign=ENG-467'
    else:  # classification search
        classifi = find_classification(classification)
        url = f'https://journals.plos.org/plosbiology/search?filterJournals={classifi}&unformattedQuery=(' \
              f'everything%3At-test)%20AND%20everything%3A{keyword}&q=(everything%3At-test)%20AND%20everyth' \
              f'ing%3A{keyword}&sortOrder=DATE_NEWEST_FIRST&page={current_page}&utm_content=a&utm_campaign=ENG-467'
    articles = get_all_articles(url)
    if tag:  # get first article in date range
        for k, v in articles.items():
            published_time_format = datetime.strptime(v['published_time'], '%d %B %Y')
            if published_time_format <= d:
                article = v
                break
    else:
        for k, v in reversed(list(articles.items())):
            published_time_format = datetime.strptime(v['published_time'], '%d %B %Y')
            if published_time_format >= d:
                article = v
                break

    # output in console
    if tag:
        print(f"the first article published on or after {date} for url '{url}' is on page {current_page} found")
    else:
        print(f"the last article published on or before {date} for url '{url}' is on page {current_page} found")
    return {'page': current_page, 'article': article}


def get_all_articles(url):
    """
    get the article title, Publish time, authors, links within a page
    :param url: the link of pagination
           for example: https://biotechnologyforbiofuels.biomedcentral.com/articles?tab=keyword&searchType=journalSearch&sort=Relevance&query=t-test&page=2
    :return: a dictionary results. results[titles[i]] = {'title': titles[i], 'published_time': times[i], 'url': links[i], 'authors': authors[i]}
    """
    results = {}
    content = handle_http_requests(url)
    soup = BeautifulSoup(content, "html.parser")
    authors = []
    authorpart = soup.find_all(attrs={"class": "search-results-authors"})
    for n in authorpart:
        authors.append(n.get_text().strip())
    times = []
    links = []
    titles = []
    pdfs = []
    titlepart = soup.find_all(attrs={"class": "search-results-title"})
    for title in titlepart:
        part = title.find('a')
        links.append("https://journals.plos.org/" + part.attrs['href'])
        pdfs.append("https://journals.plos.org/" + part.attrs['href'].replace("article", "article/file") + "&type=printable")
        titles.append(part.get_text())
    for n in range(0, 15):
        date1 = soup.find(attrs={"id": "article-result-" + str(n) + "-date"})
        if date1 is None:
            break
        else:
            date2 = date1.get_text(strip=True).replace("published ", '').replace(' ', '-')
            times.append(convert_date_format1(date2, '%d %B %Y'))
    # len(authors) = len(times) = len(links) = len(titles) = 50
    for i in range(len(authors)):
        results[titles[i]] = {'title': titles[i], 'published_time': times[i], 'url': links[i], 'pdf': pdfs[i],
                              'authors': authors[i]}
    return results


def generate_diagram(start_time, end_time, articles):
    """

    :param start_time: 01 January 2010
    :param end_time: 01 December 2012
    :param articles: {"Biomedicine":{"title": "Biomedicine", "url": "https://", "pdf": "https://", "authors": "...", "published_time": "24 Jun 2017"}}
    :return: time_stamp: If the time difference is less than or equal to one year
                         --> {'January 2010': 12, 'February 2010': 4, ...}
                         else
                         ---> {'2010': 103, '2011': 194, ...}
    """
    date1 = datetime.strptime(convert_date_format2(start_time, '%d %B %Y'), '%d %B %Y')
    date2 = datetime.strptime(convert_date_format2(end_time, '%d %B %Y'), '%d %B %Y')
    delta = (date2 - date1).days
    time_stamp = {}
    if delta > 365:
        for i, t in articles.items():
            date = datetime.strptime(t["published_time"], '%d %B %Y')
            year = str(date.year)
            if year in time_stamp:
                time_stamp[year] += 1
            else:
                time_stamp[year] = 1
    else:
        for i, t in articles.items():
            date = datetime.strptime(t["published_time"], '%d %B %Y')
            year_month = str(date.year) + '-' + str(date.month).zfill(2)
            if year_month in time_stamp:
                time_stamp[year_month] += 1
            else:
                time_stamp[year_month] = 1
    return time_stamp


def merge_diagram_articles(diagram, articles):
    """

    :param diagram:
    :param articles:
    :return:
    """
    result = {"articles": articles, "diagram": diagram}
    return result
