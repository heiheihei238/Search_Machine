import tool

html = tool.handle_http_requests('https://actaneurocomms.biomedcentral.com/articles/10.1186/s40478-021-01289-1')
print(tool.find_min_distance_between_regex_matches(html, '2', '5'))
