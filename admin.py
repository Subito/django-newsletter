from django.contrib import admin
from newsletter.models import Newsletter, NewsletterSendItem

class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'send_time', 'send_interval', 'active', 'send_next',)
    list_filter = ('send_time', 'send_interval', 'active', 'send_last',)

class NewsletterSendItemAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'date_send',)
    list_filter = ('date_send', 'content_type',)

admin.site.register(Newsletter, NewsletterAdmin)
admin.site.register(NewsletterSendItem, NewsletterSendItemAdmin)
