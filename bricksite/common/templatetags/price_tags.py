from django import template


register = template.Library()


@register.filter
def price_no_data(value, no_data='No Data'):
    return '$ ' + value if value and value != 'None' else no_data