from django import template

from mastf.MASTF.models import AbstractBaseFinding, Vulnerability
from mastf.MASTF.mixins import VulnContextMixin

register = template.Library()

@register.filter(name='split')
def split(value: str, key: str) -> list:
    """
    Returns the value turned into a list.
    """
    return value.split(key) if value else []


@register.filter(name='vuln_stats')
def vuln_stats(value):
    mixin = VulnContextMixin()
    data = {}

    mixin.apply_vuln_context(data, AbstractBaseFinding.stats(Vulnerability, base=value))
    return data

