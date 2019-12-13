import re
import urllib.parse
from itertools import cycle

import requests
from bs4 import BeautifulSoup

# for reading email from pdf
import io
from PyPDF2 import PdfFileReader
from urllib.request import urlopen

from crossref.restful import Journals
from django.utils.dateparse import parse_date
from lxml.html import fromstring
from selenium import webdriver
import time

import json

from proxy_requests.proxy_requests import ProxyRequests, ProxyRequestsBasicAuth

from metadata import getDate

regex = re.compile(("([a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`"
                    "{|}~-]+)*(@|\sat\s)(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(\.|"
                    "\sdot\s))+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)"))


def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:10]:
        # if i.xpath('.//td[7][contains(text(),"yes")]'):
        proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
        proxies.add(proxy)
    return proxies


def download_pdf(link, download_folder, path_to_chrome_driver):
    options = webdriver.ChromeOptions()
    profile = {
               "plugins.plugins_list": [{"enabled": False,
                                         "name": "Chrome PDF Viewer"}],
               "download.default_directory": download_folder,
               "download.extensions_to_open": ""
                }
    options.add_experimental_option("prefs", profile)
    driver = webdriver.Chrome(path_to_chrome_driver,chrome_options = options)
    driver.get(link)
    filename = link.split("/")[4].split(".cfm")[0]
    time.sleep(10)
    driver.close()


def pdfExtraction(contents):

    email = None
    matching = [s for s in contents if "@" in s]
    if len(matching) != 0:
        match_list = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", ''.join(matching))
        if len(match_list) > 0:
            email = ''.join(match_list)

    return email


def getEmail(eventdoi):

    doi = eventdoi
    url = 'https://dx.doi.org/' + doi
    email = ''

    try:
        r = requests.get(url)
        data = r.text
        soup = BeautifulSoup(data, "lxml" )

        for i in soup.find_all(href=re.compile("mailto")):
            email = i.string

        if email != '' and email.count('@') == 0:
            string = str(soup.find_all(href=re.compile("mailto"))[0])
            email = next(email[0] for email in re.findall(regex,string ) if not email[0].startswith('//'))

    except Exception as e:
        print("Exception in getEmail: ", e)

    if email == '':
        # print ('Email not found in webpage..!')
        email = getEmailThirdParty(doi)

    return email


def LibGen(_doi):

    email = None
    args = {"doi": _doi}
    url = "http://libgen.io/scimag/get.php?{}&downloadname=&key=WT1Y6H5KR8SE3KG4".format(urllib.parse.urlencode(args))

    try:
        page = requests.get(url)

    except Exception as e:
        print("Exception Raised in Opening the Libgen: ", e)
        return None

    if str(page.content).count("Article not found.") or str(page.content).count("504 Gateway Time-out"):
        return None

    else:
        soup = BeautifulSoup(page.content, 'html.parser')
        new_url = ""

        for link in soup.find_all('a', href=True):
            url = link['href']

            if url.startswith('http://libgen.io'):
                new_url = url.strip()

        try:

            if new_url:
                r = requests.get(new_url, stream=True)
                f = io.BytesIO(r.content)
                reader = PdfFileReader(f)
                if reader.isEncrypted:
                    reader.decrypt("")

                contents = reader.getPage(0).extractText().split('\n')
                f.close()

                email = pdfExtraction(contents)

        except Exception as e:
            print("Exception Raised", end=" ")
            print(e)

        return email


def UnPayWall(doi):

    # unpaywall
    email = None
    try:
        url = "https://api.unpaywall.org/v2/" + doi + "?email=YOUR_MAIL"
        page = urlopen(url)
        html = page.read()
        html = html.decode('windows-1252')
        html = json.loads(html)
        if html and html['best_oa_location'] and html['best_oa_location']['url_for_pdf']:

            link = html['best_oa_location']['url_for_pdf']
            r = requests.get(link, stream=True)
            f = io.BytesIO(r.content)
            reader = PdfFileReader(f)
            contents = reader.getPage(0).extractText().split('\n')
            f.close()
            email = pdfExtraction(contents)

    except Exception as e:
        print("Exception Raised: ", e)

    return email


def SciHub(doi):

    email = None
    url = 'https://sci-hub.tw/' + doi
    # download_pdf(url,"C:\\Users\\hp\\Desktop" , "F:\\chromedriver.exe")
    try:
        page = requests.get(url)
        html = page.text
        soup = BeautifulSoup(html, 'lxml')
        pdfurl = soup.find("iframe").get("src")

        if pdfurl.count("http:") == 0:
            pdfurl = "http:" + pdfurl

        r = requests.get(pdfurl, stream=True)
        f = io.BytesIO(r.content)
        reader = PdfFileReader(f)
        contents = reader.getPage(0).extractText().split('\n')
        f.close()

        email = pdfExtraction(contents)

    except Exception as e:
        print("EXCEPTION: ", e)

    return email


def getEmailThirdParty(doi):

    print("Trying Unpaywall..")
    email = UnPayWall(doi)
    if not email:
        print("Trying Libgen..")
        email = LibGen(doi)
        if not email:
            print("Trying Scihub..")
            email = SciHub(doi)

    return email


def getTotalCitations(title):

    args = {
        "q": title,
    }

    url = "https://scholar.google.co.in/scholar?hl=en&as_sdt=0%2C5&{}&0btnG=".format(urllib.parse.urlencode(args))

    proxies = get_proxies()
    proxy_pool = cycle(proxies)

    url_check = 'https://httpbin.org/ip'
    url_page = requests.get(url)

    for i in range(1, 11):
        proxy = next(proxy_pool)
        print(proxy)
        print("Request #%d" % i)
        try:
            url_page = requests.get(url, proxies={"http": proxy, "https": proxy})
            response = requests.get(url_check, proxies={"http": proxy, "https": proxy})
            print(response.json())
            break
        except:
            print("Skipping. Connnection error")

    soup = BeautifulSoup(url_page.content, 'html.parser')
    list = soup.find_all('div', class_="gs_ri")
    print("list: ", list)

    if len(list):
        encodeddiv = list[0].encode()
    else:
        return [None, None]

    soup2 = BeautifulSoup(encodeddiv, 'html.parser')
    firstdiv = soup2.find_all(href=re.compile("/scholar\?cites"))

    if len(firstdiv):
        citations = firstdiv[0].string.split(" ")[-1]
        url = "https://scholar.google.co.in" + firstdiv[0]['href']

        return [citations, url]
    else:
        return [None, None]


def getTotalCitationsForJournal(ISSN, start , end):

    if start is None:
        start = "1900-01-01"

    if end is None:
        end = "2025-12-12"

    start = parse_date(start)
    end = parse_date(end)

    journals = Journals()
    a = journals.works(ISSN).all()
    count = 0

    while True:

        try:
            b = next(a)
            date = getDate(b)
            print(date)
            if date > end or date < start:
                continue
            print(count)
            count += 1

        except StopIteration:
            break

    return count
