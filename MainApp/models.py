from django.db import models


class DOIQuery(models.Model):

    DOI = models.CharField(max_length=50)


class EmailInfo(models.Model):

    DOI = models.CharField(max_length=50)
    Email = models.EmailField(null=True, blank=True)
    Citation = models.ForeignKey(DOIQuery, on_delete=models.CASCADE)
    Date = models.DateField(null=True, blank=True)
    Author = models.CharField(max_length=1000, null=True, blank=True)
    title = models.CharField(max_length=1000, null=True, blank=True)


class JournalQuery(models.Model):

    ISSN = models.CharField(max_length=50)


class EmailInfoJournal(models.Model):

    DOI = models.CharField(max_length=50)
    Email = models.EmailField(null=True, blank=True)
    Citation = models.ForeignKey(JournalQuery, on_delete=models.CASCADE)
    Date = models.DateField(null=True, blank=True)
    Author = models.CharField(max_length=1000, null=True, blank=True)
    title = models.CharField(max_length=1000, null=True, blank=True)








