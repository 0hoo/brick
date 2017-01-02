from django import template


register = template.Library()


@register.filter
def html_placeholder(field, args=None):
    if args is None:
        return field
    field.field.widget.attrs.update({"placeholder": args})
    return field
