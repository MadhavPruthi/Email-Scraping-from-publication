from django.contrib import admin
from .models import EmailInfo, DOIQuery, EmailInfoJournal, JournalQuery
# Register your models here.

admin.site.register(EmailInfo)
admin.site.register(DOIQuery)
admin.site.register(JournalQuery)
admin.site.register(EmailInfoJournal)