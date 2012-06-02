import json
from datetime import timedelta, datetime, date

from django.core.management.base import BaseCommand, CommandError

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, mail_admins
from django.contrib.contenttypes.models import ContentType
from django.template import Template, Context

from newsletter.models import Newsletter, NewsletterSendItem

class Command(BaseCommand):
    args = '<no args accepted>'
    help = 'script gets called once in a while to check which newsletter should get send'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('[i] searching for newsletter...\n')
        all_newsletter = Newsletter.objects.filter(active=True, status=Newsletter.READY)
        error = open('newsletter_errors.log', 'a')
        error.write('-----------------------------------------------------------\n')
        error.write('%s\n' % datetime.now())
        error.write('-----------------------------------------------------------\n')
        log = open('newsletter.log', 'a')
        log.write('-----------------------------------------------------------\n')
        log.write('%s\n' % datetime.now())
        log.write('-----------------------------------------------------------\n')
        log.write('[i] found %s newsletter\n' % len(all_newsletter)) 
        for n in all_newsletter:
            try:
                now = datetime.now()
                time_send = True if n.send_time <= now.time() else False
                send = True if n.send_next == date.today() and time_send else False
                if not send:
                    log.write('  [i] "%s" should not get send. Skipping\n' % n.reason)
                    return
                log.write('  [i] Attempting to send "%s"\n' % n.reason)
                n.status = Newsletter.CURRENTLY_SENDING
                n.save()
                model = ContentType.objects.get(model=n.model).model_class()
                conditions = json.loads('[%s]' % n.conditions)
                r = model.objects.filter(**conditions[0])
                to = []
                recipient_attrs = n.recipient_field.split('.')
                send_items = NewsletterSendItem.objects.filter(newsletter=n)
                count_skip = 0
                for o in r: # for object in result
                    email = o
                    skip = False
                    # determine if object already got a newsletter
                    for item in send_items:
                        if item.content_type == ContentType.objects.get_for_model(o):
                            if item.object_id == o.pk:
                                count_skip += 1
                                skip = True
                    if skip:
                        continue
                    send_item = NewsletterSendItem(newsletter=n, content_object=o)
                    send_item.save()
                    attributes = []
                    for a in recipient_attrs:
                        try:
                            email = getattr(email, a)
                            attributes.append(email)
                        except AttributeError:
                            pass
                    to.append(attributes[-1])
                log.write('    [i] found %s recipients\n' % len(to))

                html = Template(n.template_code)
                raw = Template(n.template_code_raw)
                subject = Template(n.email_subject)

                successfull = 0

                for recipient in to:
                    c = Context(locals())
                    html_text = html.render(c)
                    raw_text = raw.render(c)
                    subject_text = subject.render(c)
                    # send actual email!
                    try:
                        msg = EmailMultiAlternatives(subject_text, raw_text, settings.NO_REPLY, [recipient.email])
                        msg.attach_alternative(html_text, 'text/html')
                        msg.send()
                        successfull += 1
                    except Exception, e:
                        error.write('%s\n' % e)
                n.send_next = date.today() + timedelta(n.send_interval)
                n.status = Newsletter.READY
                n.send_last = date.today()
                n.save()
                log.write('    [i] %s emails successfull\n' % successfull)
                log.write('    [i] %s recipients skipped\n' % count_skip)
            except Exception, e:
                n.status = Newsletter.ERROR
                n.save()
                error.write('%s\n' % e)
        log.close()
        error.close()
