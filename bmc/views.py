import json
import os
import requests

from django.http import HttpResponse
from django.shortcuts import render
from datetime import datetime
from bmc.webspider import webspider
from bmc.webspider import webspider2
from bmc.webspider import webspider3

import matplotlib.pyplot as plt
import io
import base64


class SaveItem:
    selectedWeb = ""
    selectedKat = ""
    kriterien = ""
    start = 0
    end = 0
    searchresult = {}
    diagram = {}
    classification = []


def welcome(request):
    return render(request, 'bmc/welcomePage.html')


# Jumping the page to searchMachine.html
def search(request, journal):
    selected = journal
    classifications = ""
    if selected == 1:
        classifications = webspider.find_classification('https://www.biomedcentral.com/journals')
        classifications.append("All")
        classifications = str(classifications)
    elif selected == 2:
        classifications = ["None"]
    else:
        classifications = webspider.find_classification("https://plos.org/")
        SaveItem.classification = classifications
        classifications.append("All")
        classifications = str(classifications)
    return render(request, 'bmc/searchMachine.html', {"journal": journal, "classification": json.dumps(classifications)})


# # Change the content of the second drop-down box after the first one has been selected
# def after_select(request):
#     selected = request.GET['value']
#     if selected == 'BMC-Journal':
#         classifications = webspider.find_classification('https://www.biomedcentral.com/journals')
#         classifications = str(classifications)
#         return HttpResponse(classifications)
#     elif selected == 'Science-Translational-Medicine':
#         res = {"None": "None"}
#         return HttpResponse(json.dumps(res))
#     else:
#         classifications = webspider.find_classification("https://plos.org/")
#         classifications = str(classifications)
#         return HttpResponse(classifications)


# Call the webspider to search the result and transfer to the front-end
def result(request, journal):
    selectedWeb = request.GET['selectedWeb']
    selectedKat = request.GET['selectedKat']
    kriterien_min = request.GET['kriterien_min']
    kriterien_max = request.GET['kriterien_max']
    start = request.GET['start']
    end = request.GET['end']
    results = {}
    if selectedWeb == "BMC-Journal":
        if selectedKat == "All":
            results = webspider.search_bmc2(kriterien_min, kriterien_max, start_time=start, end_time=end)
        else:
            results = webspider.search_bmc(kriterien_min, kriterien_max, classification=selectedKat, start_time=start, end_time=end)
    elif selectedWeb == "PLOS":
        results = webspider3.search_plos(classification=find_selectedKat_num(str(selectedKat)), start_time=start, end_time=end, keyword='n')
    elif selectedWeb == "Science-Translational-Medicine":
        results = webspider2.search_science(start, end, kriterien_min, kriterien_max)
    searchresult = {'results': results, 'resultnumber': len(results['articles']), 'kriterien': 'n = '+kriterien_min+' - '+kriterien_max,
                    'selectedKat': selectedKat}
    SaveItem.searchresult = results
    SaveItem.selectedWeb = selectedWeb
    SaveItem.selectedKat = selectedKat
    SaveItem.kriterien = 'n = '+kriterien_min+' - '+kriterien_max
    SaveItem.start = start
    SaveItem.end = end
    SaveItem.diagram = results['diagram']
    return HttpResponse(json.dumps(searchresult))


def find_selectedKat_num(selectedKat):
    n = 0
    for p in SaveItem.classification:
        if p == selectedKat:
            return n
        else:
            n += 1
    return 12


# Save the result and the condition information in workspace
def save(request, journal):
    data = ["Journal:" + SaveItem.selectedWeb, "Classify: " + SaveItem.selectedKat, "Criteria: " + SaveItem.kriterien,
            "start "
            "time: " + SaveItem.start.__str__(), "end time: " + SaveItem.end.__str__()]
    result = SaveItem.searchresult
    n = 1
    while os.path.exists("savedResult " + str(n) + ".txt"):
        n += 1
    filename = "savedResult " + str(n) + ".txt"
    with open(filename, "w", encoding="utf-8") as file:
        for line in data:
            file.write(line + "\n")
    with open(filename, "a", encoding="utf-8") as file:
        article_num = 1
        for key in result['articles']:
            file.write("\n")
            file.write("Article" + str(article_num) + ":\n")
            file.write("Title: " + result['articles'][key]['title'] + "\n")
            file.write("Published date: " + result['articles'][key]['published_time'] + "\n")
            file.write("Author: " + result['articles'][key]['authors'] + "\n")
            file.write("Link: " + result['articles'][key]['url'] + "\n")
            file.write("PDF link: " + result['articles'][key]['pdf'] + "\n")
    print("saved successfully")
    return HttpResponse("Successfully")


# Download all the selected pdf in a special folder in the workspace
def download_pdf(request, journal):
    index = request.GET['index']
    selected = eval('[' + index + ']')
    print(selected)
    path = os.getcwd()
    timedate = datetime.now().date().__str__().replace("-", "_") + "_" + datetime.now().strftime("%H_%M_%S")
    if not os.path.exists(timedate):
        os.mkdir(path + "\\" + timedate)
        location = 0
        article_num = 1
        for i in SaveItem.searchresult['articles']:
            if location in selected:
                response = requests.get(SaveItem.searchresult['articles'][i]['pdf'])
                bytes_io = io.BytesIO(response.content)
                with open(path + "\\" + timedate + "\\" + "Article " + str(article_num) + ".PDF", mode='wb') as f:
                    f.write(bytes_io.getvalue())
                article_num += 1
            location += 1
    print("download successfully")
    return HttpResponse("Successfully")


# Show the statistical result of the Search
def static_result(request, journal):
    x = list(SaveItem.diagram.keys())
    print(x)
    y = list(SaveItem.diagram.values())
    print(y)
    plt.bar(x, y)
    plt.xticks(rotation=90)

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    base64_image = base64.b64encode(buffer.getvalue()).decode()

    context = {'chart_data': base64_image}
    return render(request, 'bmc/static.html', context)
