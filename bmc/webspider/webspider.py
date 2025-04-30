import time
import datetime

from bmc.webspider import tool
from bs4 import BeautifulSoup


def find_classification(url):
    """

    :param url: the link of the homepage
           for example: https://www.biomedcentral.com/journals
    :return: a list of classification_name: [string]
    """

    content = tool.handle_http_requests(url)
    soup = BeautifulSoup(content, "html.parser")

    if url == 'https://www.biomedcentral.com/journals':
        classification_name = [name.string.replace(' ', '-') for name in soup.find_all('h3')]

        classification_name.pop()
        return classification_name

    elif url == 'https://plos.org/':
        text = soup.find_all(attrs={'class': 'elementor-text-editor elementor-clearfix'})
        classification_name = []
        for a in text:
            if a.find('a'):
                for b in a.find_all('a'):
                    classification_name.append(b.get_text().replace(' ', '_'))
        classification_name.pop()
        classification_name.pop()
        classification_name.pop()
        return classification_name

    else:
        pass


def search_bmc(small_n, big_n, classification='', start_time='01/01/2022', end_time=time.strftime('%m/%d/%Y', time.localtime())):
    """
    classification search
    :param classification: string.  id of the classification. for example: "Criminology-and-Criminal-Justice"
    :param start_time: datetime.date
    :param end_time: datetime.date
    :param small_n: String
    :param big_n: String
    :return: results: dictionary
            {'diagram':{'2017-05': 1, '2017-11': 2, '2017-02': 1, '2017-04': 2, '2017-10': 2},
             'articles':{'BMP8A sustains spermatogenesis by activating both SMAD1/5/8 and SMAD2/3 in spermatogonia':
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
            }
    """
    start_time_format = datetime.datetime.strptime(start_time, "%m/%d/%Y").strftime("%d %B %Y")
    end_time_format = datetime.datetime.strptime(end_time, "%m/%d/%Y").strftime("%d %B %Y")
    articles = {}
    classification_urls = tool.get_sub_classification_urls(classification)
    for classification_url in classification_urls:
        all_articles = tool.get_articles_by_date_range(start_time_format, end_time_format)
        articles.update(tool.get_related_articles(all_articles, small_n, big_n))
        print("search for " + tool.get_url_without_property(classification_url) + " complete")
    diagram = tool.generate_diagram(start_time_format, end_time_format, articles)
    results = tool.merge_diagram_articles(diagram, articles)
    return results


def search_bmc2(small_n, big_n, start_time='01/01/2022', end_time=time.strftime('%m/%d/%Y', time.localtime())):
    """
    global search
    :param start_time: datetime.date
    :param end_time: datetime.date
    :param small_n: string
    :param big_n: string
    :return: result: dictionary
            {'diagram':{'2017-05': 1, '2017-11': 2, '2017-02': 1, '2017-04': 2, '2017-10': 2},
             'articles':{'BMP8A sustains spermatogenesis by activating both SMAD1/5/8 and SMAD2/3 in spermatogonia':
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
            }
    """
    start_time_format = datetime.datetime.strptime(start_time, "%m/%d/%Y").strftime("%d %B %Y")
    end_time_format = datetime.datetime.strptime(end_time, "%m/%d/%Y").strftime("%d %B %Y")
    all_articles = tool.get_articles_by_date_range(start_time_format, end_time_format)
    articles = tool.get_related_articles(all_articles, small_n, big_n)
    diagram = tool.generate_diagram(start_time_format, end_time_format, articles)
    result = tool.merge_diagram_articles(diagram, articles)
    return result
