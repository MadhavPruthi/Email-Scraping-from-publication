import urllib.parse

from django.db import transaction
from django.forms import model_to_dict
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from crossref.restful import Works, Journals
from bs4 import BeautifulSoup
import requests
from MainApp.models import EmailInfo, DOIQuery, JournalQuery, EmailInfoJournal
import metainfoscrapper
from API import GetDoiByTitle
import metadata
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
from MainApp.tasks import mailFetch, mailFetchJournal

works = Works()
journals = Journals()


def byDOI(request):

    query = request.GET.get("q")
    citation_urls = request.GET.get("c")

    if query:

        response = works.doi(query)

        if response is None:
            return JsonResponse({"response": "DOI is not valid", "done":"no"})

        if not DOIQuery.objects.filter(DOI__exact=query).exists():
            citation = DOIQuery(DOI=query)
            citation.save()

        if citation_urls:
            main_url = citation_urls
        else:
            return JsonResponse({"response":"No citations found!", "done":"no"})

        mailFetch(query, main_url)

        context = {}

        return JsonResponse(context)

    else:
        return render(request, 'home.html', {})


def byJournal(request):

    query = request.GET.get('q')
    start = request.GET.get('s')
    end = request.GET.get('e')

    if start is None:
        start = "1900-01-01"

    if end is None:
        end = "2025-12-12"

    if query:

        mailFetchJournal(query, start, end )

        context = {"done": "no"}

        return JsonResponse(context)

    return render(request, 'journalFetch.html', {})


@csrf_exempt
def Emails(request):

    DOI = request.POST.get("info")
    with transaction.atomic():
        emails = EmailInfo.objects.filter(Citation__DOI__exact=DOI)
    return render(request, 'emails.html', {'MailList': emails})


@csrf_exempt
def EmailsJournal(request):

    ISSN = request.POST.get("info")
    emails = EmailInfoJournal.objects.filter(Citation__ISSN__exact=ISSN)
    return render(request, 'emails.html', {'MailList': emails})


def ShowDOIEmails(request, string):

    doi = urllib.parse.unquote(string)
    citation = DOIQuery.objects.get(DOI__exact=doi)
    MailList = EmailInfo.objects.filter(Citation=citation)
    ValidEmailsSize = EmailInfo.objects.filter(Citation=citation, Email__isnull=False).count()

    context = {
        "MailList":MailList,
        "TotalSize":MailList.count(),
        "ValidEmailsSize":ValidEmailsSize,
    }
    return render(request, 'home.html', context)


def ShowJournalEmails(request, string):


    ISSN = urllib.parse.unquote(string)
    citation = JournalQuery.objects.get(ISSN__exact=ISSN)
    MailList = EmailInfoJournal.objects.filter(Citation=citation)
    ValidEmailsSize = EmailInfoJournal.objects.filter(Citation=citation, Email__isnull=False).count()

    context = {
        "MailList":MailList,
        "TotalSize":MailList.count(),
        "ValidEmailsSize":ValidEmailsSize,
    }
    return render(request, 'journalFetch.html', context)


def TotalCitations(request):

    q = request.GET.get("q")
    response = works.doi(q)
    title = response['title']

    author = metadata.getAuthor(response)
    date = metadata.getDate(response)
    totalCitations = metainfoscrapper.getTotalCitations(q)
    citation_urls = metainfoscrapper.getTotalCitations(q)[1]

    print(citation_urls)
    print(totalCitations)

    totalCitations = totalCitations[0]

    print(author, date, title[0])
    context = {"totalCitations":totalCitations, "title":title[0], "author":author, "date":date, "citation_urls":citation_urls}

    return JsonResponse(context)


def TotalCitationsJournal(request):

    q = request.GET.get("q")
    a = journals.works(q).count()

    totalCitations = a
    context = {
        "totalCitations":totalCitations,
    }

    return JsonResponse(context)