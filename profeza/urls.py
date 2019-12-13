from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
import MainApp.views as MainViewIndex

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^$', TemplateView.as_view(template_name='homepage.html')),
    url(r'^journal/$', MainViewIndex.byJournal , name="journal"),
    url(r'^finalDOI/', MainViewIndex.ShowDOIEmails, name="showdoiemails"),
    url(r'^emailjournal/$', MainViewIndex.EmailsJournal, name="emailjournal"),
    url(r'^main/', MainViewIndex.byDOI , name="index"),
    url(r'^emails/$', MainViewIndex.Emails , name="emails"),
    url(r'^emailjournal/(?P<string>.+)/$', MainViewIndex.ShowJournalEmails, name="showjorunalmails"),
    url(r'^totalcitations/', MainViewIndex.TotalCitations, name="totalCitations"),
    url(r'^totalcitationsjournal/', MainViewIndex.TotalCitationsJournal, name="totalcitationsjournal"),
]
