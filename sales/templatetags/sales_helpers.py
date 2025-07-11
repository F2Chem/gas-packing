import datetime

from django import template
from django.utils.html import mark_safe

from sales.models import *

register = template.Library()




@register.filter
def select_option(line, spec):
    if line.spec_id == spec.id:
        return mark_safe(' selected="selected"')
    else:
        return ''



@register.filter
def checkbox(spec, customer):
    print('helper')
    print(spec)
    print(type(spec))
    
    s = f'<input type="checkbox" id="spec{spec.id}" name="spec{spec.id}"'
    if spec.customer_set.filter(id=customer.id).exists():
        s += ' checked'
    s += '/>'
    return mark_safe(s)
