""" Getting Meta Data """
from django.utils.dateparse import parse_date


def getAuthor(response):
    try:
        authorlist = response['author']
        allauthors = ""

        for json in authorlist:
            allauthors += json['given'] + " " + json['family']
            allauthors += ", "

        allauthors = allauthors[:-2]
        author = allauthors
    except:
        author = None

    return author


def getDate(response):
    try:
        created = response['created']['date-parts'][0]
        temp = ""
        for i in created:
            temp += str(i) + "-"

        date = temp[:-1]
        date = parse_date(date)

    except:
        date = None

    return date