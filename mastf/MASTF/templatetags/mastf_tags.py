from django import template
from django.urls import get_resolver

from mastf.MASTF.models import AbstractBaseFinding, Vulnerability
from mastf.MASTF.mixins import VulnContextMixin
from mastf.MASTF.utils.enum import ComponentCategory

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


@register.filter(name='component_color')
def component_color(category) -> str:
    if category == ComponentCategory.ACTIVITY:
        return 'green'
    elif category == ComponentCategory.PROVIDER:
        return 'red'
    elif category == ComponentCategory.SERVICE:
        return 'yellow'
    elif category == ComponentCategory.RECEIVER:
        return 'orange'

    return 'secondary'


@register.filter(name="allobjects")
def allobjects(manager):
    return list(manager.all())