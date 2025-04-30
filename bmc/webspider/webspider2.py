from bmc.webspider import tool2


def search_science(start_time, end_time, small_n, big_n):
    """
    :param start_time: "01/01/2021"
    :param end_time: "12/31/2021"
    :param small_n: String
    :param big_n: String
    :return: result:
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
    articles = {}
    diagram = {}
    format_start_time = tool2.convert_date_form(start_time)
    format_end_time = tool2.convert_date_form(end_time)
    period_list = tool2.generate_period_tuple(format_start_time, format_end_time)
    keyword = tool2.generate_keyword(small_n, big_n)
    for period in period_list:
        url = tool2.generate_url(period[0], period[1], keyword)
        html = tool2.handle_http_requests2(url)
        last_related_article = tool2.get_last_related_article(url, html, small_n, big_n)
        articles.update(tool2.get_all_related_article(period[0], period[1], keyword, last_related_article))
        diagram.update(tool2.generate_diagram(period[0], period[1], articles))
    result = tool2.merge_diagram_articles(diagram, articles)
    return result
