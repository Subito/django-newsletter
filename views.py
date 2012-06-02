from django.utils.translation import ugettext as _
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.template import Template, Context
import json

from django.contrib.admin.models import User

from newsletter.models import Newsletter

def test(request, n_id=None):
    if not n_id:
        raise Http404
    newsletter = get_object_or_404(Newsletter, pk=n_id)
    model = ContentType.objects.get(model=newsletter.model).model_class()
    dict = json.loads('[%s]' % newsletter.conditions)
    r = model.objects.filter(**dict[0])
    all_addr = []
    attr = newsletter.recipient_field.split('.')
    for o in r:
        dummy = o
        all_attr = []
        for a in attr:
            try:
                dummy = getattr(dummy, a)
                all_attr.append(dummy)
            except AttributeError:
                pass
        all_addr.append(all_attr[-1])
    t = Template(newsletter.template_code)
    c = Context(locals())
    return HttpResponse(t.render(c))
