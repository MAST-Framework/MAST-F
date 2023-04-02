from django import template

register = template.Library()

@register.filter(name='split')
def split(value: str, key: str) -> list:
    """
    Returns the value turned into a list.
    """
    return value.split(key)