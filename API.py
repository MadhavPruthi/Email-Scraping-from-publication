import re
import urllib.parse
from crossref.restful import Works
import subprocess
from bs4 import BeautifulSoup
import requests
from MainApp.models import EmailInfo
import scholar
import metainfoscrapper

citation_urls = []
works = Works()


"""
def ScholarCheck():

    querier = scholar.ScholarQuerier()
    settings = scholar.ScholarSettings()
    querier.apply_settings(settings)

    query = scholar.SearchScholarQuery()
    query.set_author("albert einstein")
    # query.set_words("On the quantum theory of radiation")
    query.set_num_page_results(1)

    querier.send_query(query)
    # Print the URL of the first article found
    print(querier.articles)
"""

def GetDoiByTitle(title):

    args = {"q": title}
    url = "https://search.crossref.org/?{}".format(urllib.parse.urlencode(args))
    # print(url)
    url_page = requests.get(url)
    soup = BeautifulSoup(url_page.content, 'html.parser')
    list = soup.find_all(href=re.compile("https://doi.org/"))

    match = re.search("(?P<url>https?://[^\s]+)", str(list[0]))
    if match is not None:
        return match.groups(0)[0][16:-2]
    return None


def get_citations(title):

    command = "python scholar.py -c 1 -A " +  "\"" + str(title[0]) + "\""
    # print(command)
    result = subprocess.check_output(command, shell=True)
    if str(result) == "'b'":
        print("Result fetching Error! IP blocking!")
        return None

    a = result.decode('windows-1252')

    strings = a.split(" ")
    for string in strings:
        if string.startswith('http://scholar.google.com/scholar?cites'):
            string = string.strip()
            citation_urls.append(string)

    main_url = citation_urls[0]
    i = 0

    while True:

        url = main_url.split('?')
        url.insert(1, "?start=" + str(i) + "&")
        url = ''.join(url)
        page = requests.get(url)

        soup = BeautifulSoup(page.content, 'html.parser')
        citation_list = soup.find_all('h3', class_='gs_rt')
        if not citation_list:
            break

        for paper in citation_list:
            name = paper.get_text()
            if name[0] == '[':
                name = name.split(' ', 1)[1]

            _doi = GetDoiByTitle(name)
            email = metainfoscrapper.getEmail(_doi)

        i += 10


def mainSearch(_doi):
    return get_citations(works.doi(_doi)['title'])

# print(mainSearch("10.1007/978-3-322-91080-6_6"))
# print(mainSearch("10.1073/pnas.1306145110"))
# print(works.doi('10.1590/0102-311x00133115'))

# ScholarCheck()