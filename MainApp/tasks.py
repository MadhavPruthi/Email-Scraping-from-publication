import requests
from background_task import background
from bs4 import BeautifulSoup
from crossref.restful import Works, Journals
from django.db import transaction
from django.utils.dateparse import parse_date

import metadata
import metainfoscrapper
from API import GetDoiByTitle
from MainApp.models import EmailInfo, DOIQuery, JournalQuery, EmailInfoJournal

works = Works()
journals = Journals()


@background(schedule=2)
def mailFetch(doi, main_url):

    i = 0

    while True:
        url = main_url.split('?')
        url.insert(1, "?start=" + str(i) + "&")
        url = ''.join(url)
        print(url)
        page = requests.get(url)

        soup = BeautifulSoup(page.content, 'html.parser')
        citation_list = soup.find_all('h3', class_='gs_rt')

        if not citation_list:
            break

        for paper in citation_list:
            name = paper.get_text()

            if name == "":
                continue

            if name[0] == '[':
                name = name.split(' ', 1)[1]

            _doi = GetDoiByTitle(name)

            if not EmailInfo.objects.filter(Citation__DOI__exact=doi, DOI__exact=_doi).exists():
                saveArticle(_doi, doi)

        i += 10


@background(schedule=1)
def saveArticle(_doi, doi):

        response = works.doi(_doi)

        # Getting metadata

        title = response['title']
        author = metadata.getAuthor(response)
        date = metadata.getDate(response)
        email = metainfoscrapper.getEmail(_doi)

        with transaction.atomic():
            citation = DOIQuery.objects.get(DOI__exact=doi)
            c = EmailInfo(DOI=_doi, Email=email, Citation=citation, title=title, Author=author, Date=date)
            c.save()


@background(schedule=3)
def mailFetchJournal(ISSN, start, end):

    query = ISSN

    a = journals.works(query).all()  # .filter(from_issued_date='2019').filter(until_pub_date='2019').all()

    if not JournalQuery.objects.filter(ISSN__exact=query).exists():
        citation = JournalQuery(ISSN=query)
        citation.save()

    while True:

        try:
            b = next(a)
            _doi = b['DOI']
            print(_doi)

            if not EmailInfoJournal.objects.filter(Citation__ISSN__exact=query, DOI__exact=_doi).exists():
                saveArticleJournal(ISSN, _doi, start, end)

        except StopIteration:
            break


@background(schedule=1)
def saveArticleJournal(ISSN, _doi, start, end):

    citation = JournalQuery.objects.get(ISSN__exact=ISSN)
    response = works.doi(_doi)
    author = metadata.getAuthor(response)
    date = metadata.getDate(response)

    start = parse_date(start)
    end = parse_date(end)

    if date > end or date < start:
        return

    title = response['title']
    email = metainfoscrapper.getEmail(_doi)
    c = EmailInfoJournal(DOI=_doi, Email=email, Citation=citation, Author=author, title=title, Date=date)
    c.save()