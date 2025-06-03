import datetime

from django import template
from django.utils.html import mark_safe

from cylinders.models import CylinderEventMetaDatum

register = template.Library()





@register.simple_tag
def cylinder_actions(obj):
    meta = obj.last_event().cylinder_event_meta_datum
    print('=============================')
    print(meta.next)
    options = meta.next.split(' ')
    s = ''
    for opt in options:
        if not opt:
            continue
        print(opt)
        print(int(opt))
        md = CylinderEventMetaDatum.objects.get(id=int(opt))
        s += ' [ <a href="/cylinders/cylinder_event_meta_datum/' + opt + '/create_event/' + str(obj.id) + '">' + md.name + '</a> ]'
    return mark_safe(s)





