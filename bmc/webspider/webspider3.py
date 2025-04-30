import time
from bmc.webspider import tool3


def search_plos(classification=0, start_time='01/01/2022', end_time=time.strftime('%m/%d/%Y', time.localtime()), keyword=''):
    """
    :param classification:
    :param start_time: datetime.date
    :param end_time: datetime.date
    :param keyword: string
    :return: result: dictionary
            {'diagram':{'2017-05': 1, '2017-11': 2, '2017-02': 1, '2017-04': 2, '2017-10': 2},
             'articles':{'BMP8A sustains spermatogenesis by activating both SMAD1/5/8 and SMAD2/3 in spermatogonia':
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
            }
    """
    all_articles = tool3.get_articles_by_date_range(start_time, end_time, keyword, classification)
    articles = tool3.get_related_articles(all_articles, keyword)
    diagram = tool3.generate_diagram(start_time, end_time, articles)
    result = tool3.merge_diagram_articles(diagram, articles)
    print(result)
    return result
