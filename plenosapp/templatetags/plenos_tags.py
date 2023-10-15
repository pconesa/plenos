# Tags (Maybe to move somewhere else)?
from django import template
register = template.Library()


@register.filter()
def get(value, index):
    return value[index]