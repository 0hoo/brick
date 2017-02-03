import time
from datetime import datetime
from django import template
from django.template import defaultfilters

register = template.Library()


def date_time_milliseconds(date_or_datetime):
    date_time = date_or_datetime.date() if isinstance(date_or_datetime, datetime) else date_or_datetime
    return int(time.mktime(date_time.timetuple()) * 1000)


@register.simple_tag
def generate_c3_array(entries, field, label, is_date=False):
    result = "['%s', " % label
    for entry in entries:
        value = defaultfilters.default_if_none(getattr(entry, field), 0) if not is_date else date_time_milliseconds(getattr(entry, field))
        result += '%s, ' % value
    result += ']'
    return result


@register.simple_tag
def generate_c3_pie_array(entries, label, field):
    result = '['
    for entry in entries:
        result += "['%s', %s], " % (entry[label], entry[field])
    result += ']'
    return result


@register.simple_tag
def generate_c3_pie_array_dict(dict_items):
    result = '['
    for k, v in dict_items:
        result += "['%s', %s], " % (k, v)
    result += ']'
    return result
