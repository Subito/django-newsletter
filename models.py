from datetime import datetime, timedelta, date

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

class Newsletter(models.Model):
    INACTIVE = 1
    CURRENTLY_SENDING = 2
    READY = 3
    ERROR = 4
    STATUS_CHOICES = (
        (INACTIVE, 'Inactive'),
        (CURRENTLY_SENDING, 'Currently sending...'),
        (READY, 'Ready'),
        (ERROR, 'Error'),
        )
    send_time = models.TimeField(help_text='The time, this newsletter should start sending')
    send_interval = models.FloatField(default=7.0, help_text='normalized to days')
    reason = models.CharField(max_length=100, help_text='short description, why this newsletter exists')
    model = models.ForeignKey(ContentType, help_text='To which model should the conditions get applied? (used as "o")')
    recipient_field = models.CharField(max_length=200, help_text='Relative path from "o" to instance of "User"')
    conditions = models.TextField(help_text='Who will receive the newsletter? The conditions in JSON format.')
    email_subject = models.CharField(max_length=100, help_text='Subject for the mail getting sent')
    template_code = models.TextField(help_text='The combined CSS & HTML code for the newsletter. Matches are in "r"')
    template_code_raw = models.TextField(help_text='The template code for raw emails')
    active = models.BooleanField(default=False, help_text='Should this newsletter get send?')
    status = models.IntegerField(choices=STATUS_CHOICES, default=INACTIVE)
    send_last = models.DateField(null=True, blank=True, help_text='The date, the last bunch was send.')
    send_next = models.DateField(null=True, blank=True, help_text='The date, the next bunch gets send.')

    def __unicode__(self):
        return '<Newsletter %s>' % self.reason

    def save(self, **kwargs):
        if not self.send_next:
            self.send_next = date.today() + timedelta(self.send_interval)
        super(Newsletter, self).save(**kwargs)

class NewsletterSendItem(models.Model):
    newsletter = models.ForeignKey(Newsletter)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    date_send = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '<Send at %s>' % self.date_send
