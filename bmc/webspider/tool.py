from datetime import datetime
import re

import requests
from bs4 import BeautifulSoup


def handle_http_requests(url):
    """
    Handle network requests
    :param url: string
    :return: response.text
    """
    try:
        response = requests.get(url)
        content = ''
        if response.status_code == 200:
            content = response.text
        else:
            print("Failed to fetch the URL " + url + ", status code:" + str(response.status_code))
    except requests.exceptions.RequestException as e:
        print(f'an error occurred when visiting {url}, the error is {e}')
        content = ''
    return content


def get_sub_classification_urls(classification):
    """
    get subclassification of a super classification
    :param the id of classification: string
           for Example: 'Criminology-and-Criminal-Justice'
    :return: dic of url of articles pagination
             an element in the list: 'https://crimesciencejournal.biomedcentral.com/'
    """

    url = "https://www.biomedcentral.com/journals"
    content = handle_http_requests(url)
    soup = BeautifulSoup(content, "html.parser")
    target_li = soup.find(id=classification)
    a_list = target_li.select('li li a:nth-of-type(1)')
    href_list = ['http:' + a['href'] + '/' for a in a_list]
    return href_list


def get_links_of_all_pages(url):
    """
    to get how many page of articles and return the links of all pages as a list
    :param url: a concrete link that from a classification pagination
           for Example: https://crimesciencejournal.biomedcentral.com/articles
    :return: the link list of all pages in this classification
             an element in the list: https://crimesciencejournal.biomedcentral.com/articles?searchType=journalSearch&sort=PubDate&page=2
    """

    url_list = []
    content = handle_http_requests(url)

    # how many pages in this concrete classification
    soup = BeautifulSoup(content, "html.parser")
    li_list = soup.find_all(name='li', class_='c-pagination__item')
    pages = int(li_list[-2].find_all(['span', 'a'])[0].text.strip())
    # modify url of all pages
    for page in range(pages):
        # url_list.append(url + '?searchType=journalSearch&sort=PubDate&page=' + str(page + 1))
        url_list.append(url + '&page=' + str(page + 1))
    return url_list


def get_url_without_property(url):
    """
    Remove the property part of the UR
    :param url: string
    :return: url: string
    """
    return url.partition('?')[0]


def get_all_articles(url):
    """
    get the article title, Published time, authors, URL and URL of pdf within a page
    :param url: the link of pagination
           for example: https://biotechnologyforbiofuels.biomedcentral.com/articles?tab=keyword&searchType=journalSearch&sort=Relevance&query=t-test&page=2
    :return: a dictionary results. results[titles[i]] = {'title': titles[i], 'published_time': times[i], 'url': links[i], 'authors': authors[i]}
    """
    results = {}
    content = handle_http_requests(url)
    soup = BeautifulSoup(content, "html.parser")
    authors = [author.text for author in soup.find_all("span", class_='c-listing__authors-list')]
    times = [pub_time.text for pub_time in soup.find_all(attrs={"itemprop": "datePublished"})]
    if 'articles?' in url:  # classification search
        links = [get_url_without_property(url).replace('/articles', '') + a['href'] for a in
                 soup.find_all(name='a', itemprop='citation')]
    else:  # global search
        links = ["https:" + a['href'] for a in soup.find_all(name='a', itemprop='citation')]
    pdfs = [li.replace('/articles', '/counter/pdf') + '.pdf' for li in links]
    titles = [title.text for title in soup.find_all('a', attrs={'data-test': 'title-link'})]
    # len(authors) = len(times) = len(links) = len(titles) = 50
    for i in range(len(authors)):
        results[titles[i]] = {'title': titles[i], 'published_time': times[i], 'url': links[i], 'pdf': pdfs[i], 'authors': authors[i]}
    return results


def search_keyword(url, keyword):
    """
    use the search engine that comes with the page
    :param keyword: search keyword
           for example: https://actaneurocomms.biomedcentral.com/articles
    :param url: a concrete link that from a classification pagination
    :return: all article links that be found with the keyword. [string]
    """
    url = url + '?tab=keyword&searchType=journalSearch&sort=Relevance&query=' + keyword
    articles = {}
    pages = get_links_of_all_pages(url)
    for page in pages:
        article = get_all_articles(page)
        articles.update(article)
    return articles


def keyword_is_in(url, keyword):
    """
    Determine if the keyword is present in the article
    :param url: the link of the article
    :param keyword: User-defined keyword
    :return: boolean
    """
    content = handle_http_requests(url)
    soup = BeautifulSoup(content, "html.parser")
    results = soup.find_all(string=re.compile(keyword))
    if len(results) == 0:
        return False
    else:
        return True


def intersection(dict1, dict2):
    """
    The intersection of two dictionary
    :param dict1:
    :param dict2:
    :return: res: list
    """
    s = set(dict1.keys()) & set(dict2.keys())
    results = dict1.copy()
    for ele in dict1:
        if ele not in s:
            del results[ele]
    return results


def get_articles_by_date_range(start_time, end_time, url="https://www.biomedcentral.com/"):
    """
    All articles with "t-test" and the keyword inputted by user within the specified date range
    will be found in this method
    :param url: the first page of pagination. The default value belong to global search
    :param start_time: '01 January 2010'
    :param end_time: '01 February 2012'
    :param small_n: String
    :param big_n: String
    :return: articles:dict
    {'BMP8A sustains spermatogenesis by activating both SMAD1/5/8 and SMAD2/3 in spermatogonia':
        {'title': 'BMP8A sustains spermatogenesis by activating both SMAD1/5/8 and SMAD2/3 in spermatogonia',
         'url': 'https://www.science.org/doi/10.1126/scisignal.aal1910',
         'pdf': 'https://www.science.org/doi/pdf/10.1126/scisignal.aal1910?download=true',
         'authors': 'by Fang-Ju Wu, Ting-Yu Lin, Li-Ying Sung, Wei-Fang Chang, Po-Chih Wu, Ching-Wei Luo',
         'published time': '02 May 2017'},
     'Arabidopsis ATXR2 deposits H3K36me3 at the promoters of LBD genes to facilitate cellular dedifferentiation':
        {'title': 'Arabidopsis ATXR2 deposits H3K36me3 at the promoters of LBD genes to facilitate cellular dedifferentiation',
         'url': 'https://www.science.org/doi/10.1126/scisignal.aan0316',
         'pdf': 'https://www.science.org/doi/pdf/10.1126/scisignal.aan0316?download=true',
         'authors': 'by Kyounghee Lee, Ok-Sun Park, Pil Joon Seo',
         'published time': '28 Nov 2017'}, ...
    }
    """
    results = {}
    last_article = binary_search_for_article(start_time, 'n', False, url=url)
    first_article = binary_search_for_article(end_time, 'n', True, url=url)
    first_page = int(first_article['page'])
    last_page = int(last_article['page'])
    end_date = datetime.strptime(end_time, '%d %B %Y')
    start_date = datetime.strptime(start_time, '%d %B %Y')

    # get valid articles in the first and the last page
    # Get the articles according to a date range in a page
    if url == "https://www.biomedcentral.com/":  # global search
        url1 = f'{url}search?searchType=publisherSearch&sort=PubDate&page={first_page}&query=t-test+n'
        url2 = f'{url}search?searchType=publisherSearch&sort=PubDate&page={last_page}&query=t-test+n'
    else:  # classification search
        url1 = f'{url}articles?tab=keyword&searchType=journalSearch&sort=PubDate&query=t-test+n&page={first_page}'
        url2 = f'{url}articles?tab=keyword&searchType=journalSearch&sort=PubDate&query=t-test+n&page={last_page}'
    x1 = get_all_articles(url1)
    x2 = get_all_articles(url2)
    merged_articles = {**x1, **x2}
    for i, t in merged_articles.items():
        date = datetime.strptime(t["published_time"], '%d %B %Y')
        if start_date <= date <= end_date:
            results.update({i: t})

    # get articles exclude the first and the last page
    page_list = [i for i in range(first_page + 1, int(last_page))]
    if url == "https://www.biomedcentral.com/":  # global search
        url_list = [
            f"{url}search?searchType=publisherSearch&sort=PubDate&page={page}&query=t-test+n"
            for page in page_list]
    else:  # classification search
        url_list = [
            f"{url}articles?tab=keyword&searchType=journalSearch&sort=PubDate&query=t-test+n&page={page}"
            for page in page_list]
    for url in url_list:
        articles = get_all_articles(url)
        results.update(articles)
    return results


def binary_search_for_article(date, keyword, tag, url='https://www.biomedcentral.com/'):
    """
    Search for an article according to the specified date and on which page it appears
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
    d = datetime.strptime(date, '%d %B %Y')
    # get the number of total page
    if url == "https://www.biomedcentral.com/":  # global search
        url2 = f'{url}search?searchType=publisherSearch&sort=PubDate&page=1&query=t-test+{keyword}'
    else:  # classification search
        url2 = f'{url}articles?tab=keyword&searchType=journalSearch&sort=PubDate&query=t-test+{keyword}'
    html = handle_http_requests(url2)
    soup = BeautifulSoup(html, 'html.parser')
    page_a = soup.find_all('a', class_='c-pagination__link')
    pages = [p.text.strip() for p in page_a]
    if len(pages) == 0:  # there are only one page in the search results pagination
        page = 1
    else:
        page = pages[-2]
    article = {}

    # binary search
    low = 0
    high = int(page)
    current_page = high // 2
    tag1 = 0  # in order to handle particular situation
    while low <= high:
        url = f'https://www.biomedcentral.com/search?searchType=publisherSearch&sort=PubDate&page={current_page}&query=t-test+{keyword}'
        html = handle_http_requests(url)
        soup = BeautifulSoup(html, 'html.parser')
        # find the published date of the first article in one page
        times = [pub_time.text for pub_time in soup.find_all(attrs={"itemprop": "datePublished"})]
        # the published date of the first article in one page
        d1 = datetime.strptime(times[0], '%d %B %Y')
        # the published date of the last article in one page
        d2 = datetime.strptime(times[-1], '%d %B %Y')
        if current_page == page or current_page == 1:
            break
        # 1
        if d == d1 == d2:
            if tag:
                tag1 = 2
                current_page -= 1
            else:
                tag1 = 1
                current_page += 1
        # 2
        elif d == d1 > d2:
            if tag:
                tag1 = 2
                current_page -= 1
            else:
                break
        # 3
        elif d > d1 >= d2:
            # the particular situation: for example:
            # the last article of page 50: 07 Juli; the last article of page 51: 06 Juli;
            # target date: 07 Juli; tag: False
            if tag1 == 1:
                current_page -= 1
                break
            # the particular situation: for example:
            # the last article of page 50: 07 Juli; the last article of page 51: 01 Juli;
            # target date: 04 Juli;
            elif abs(high-low) == 1:
                if tag:
                    break
                else:
                    current_page -= 1
                    break
            else:
                high = current_page - 1
                current_page = (low + high) // 2
        # 4
        elif d1 > d > d2:
            break
        # 5
        elif d1 > d2 == d:
            if tag:
                break
            else:
                tag1 = 1
                current_page += 1
        # 6
        elif d1 >= d2 > d:
            # the particular situation: for example:
            # the last article of page 50: 07 Juli; the first article of page 51: 06 Juli;
            # target date: 06 Juli; tag: True
            if tag1 == 2:
                current_page += 1
                break
            # the particular situation: for example:
            # the last article of page 50: 07 Juli; the last article of page 51: 01 Juli;
            # target date: 04 Juli;
            elif abs(high-low) == 1:
                if tag:
                    current_page += 1
                    break
                else:
                    break
            else:
                low = current_page + 1
                current_page = (low + high) // 2
        else:
            print("error occurred in binary search")
            break

    # get url
    if url == "https://www.biomedcentral.com/":
        url2 = f'{url}search?searchType=publisherSearch&sort=PubDate&page={current_page}&query=t-test+{keyword}'
    else:
        url2 = f'{url}articles?tab=keyword&searchType=journalSearch&sort=PubDate&query=t-test+{keyword}&page={current_page}'
    articles = get_all_articles(url2)
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
        print(f"the first article published on or after {date} for url '{url}' is found on page {current_page}")
    else:
        print(f"the last article published on or before {date} for url '{url}' is found on page {current_page}")
    return {'page': current_page, 'article': article}


def get_related_articles(articles, small_n, big_n):
    """
    The articles are already found according to start time and end time.
    This function further filters out articles that meet the relevance criteria.
    :param articles: Information on all articles within the specified date range
    :param small_n: String
    :param big_n: String
    :return: results: dict
    """
    number = len(articles)
    current_number = 0
    results = {}
    print(f"the total number of to be tested article is {number}")
    for i, t in articles.items():
        if is_related(t['url'], small_n, big_n):
            results.update({i: t})
        current_number += 1
        if current_number % 100 == 0:
            print(f'the current process is {current_number}/{number}')
    return results


def is_related(url, small_n, big_n):
    """
    to judge if an article meets the relevance criteria
    :param url: the url of the article
    :param small_n: String
    :param big_n: String
    :return: True or False
    """
    html = handle_http_requests(url)
    if html == '':
        return False
    distance = find_min_distance_between_regex_matches(html, small_n, big_n)
    # print(f'the distance is {distance} in {url}')
    return True if distance < 2000 else False


def find_min_distance_between_regex_matches(html, small_n, big_n):
    """
    regex1: the regex of t-test
    :param html: html content
    :param small_n: String
    :param big_n: String
    :return: if no match is found, return -1. Otherwise returns the minimum distance
    """
    # Find all matches for the first regular expression
    regex1 = re.compile(r'\b(<\w+>)*t(</\w+>)*[\s-]*tests?\b', re.IGNORECASE)
    regex_patterns = []
    for n in range(int(small_n), int(big_n) + 1):
        regex_patterns.append(rf'{regex_keyword(f"n = {n}")}')
    target_indices = [m.start() for m in re.finditer(regex1, html)]
    min_distance = float('inf')
    for pattern in regex_patterns:
        match_indices = [m.start() for m in re.finditer(pattern, html)]
        if not match_indices:  # Check if there are no matches for the pattern
            continue
        for target_idx in target_indices:
            distances = [abs(target_idx - match_idx) for match_idx in match_indices]
            min_distance = min(min_distance, min(distances))
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


def generate_diagram(start_time, end_time, articles):
    """

    :param start_time: 01 January 2010
    :param end_time: 01 December 2012
    :param articles: {"Biomedicine":{"title": "Biomedicine", "url": "https://", "pdf": "https://", "authors": "...", "published time": "24 Jun 2017"}}
    :return: time_stamp: If the time difference is less than or equal to one year
                         --> {'January 2010': 12, 'February 2010': 4, ...}
                         else
                         ---> {'2010': 103, '2011': 194, ...}
    """
    date1 = datetime.strptime(start_time, '%d %B %Y')
    date2 = datetime.strptime(end_time, '%d %B %Y')
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