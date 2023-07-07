# This file is part of MAST-F's Frontend API
# Copyright (C) 2023  MatrixEditor
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from django import template
from datetime import date
from time import mktime

from mastf.MASTF.models import AbstractBaseFinding, PackageVulnerability
from mastf.MASTF.mixins import VulnContextMixin
from mastf.MASTF.utils.enum import ComponentCategory

register = template.Library()


@register.filter(name="split")
def split(value: str, key: str) -> list:
    """
    Returns the value turned into a list.
    """
    return value.split(key) if value else []


@register.filter(name="vuln_stats")
def vuln_stats(value):
    mixin = VulnContextMixin()
    data = {}

    mixin.apply_vuln_context(
        data, AbstractBaseFinding.stats(PackageVulnerability, base=list(value))
    )
    return data


@register.filter(name="component_color")
def component_color(category) -> str:
    if category == ComponentCategory.ACTIVITY:
        return "green"
    elif category == ComponentCategory.PROVIDER:
        return "red"
    elif category == ComponentCategory.SERVICE:
        return "yellow"
    elif category == ComponentCategory.RECEIVER:
        return "orange"

    return "secondary"


@register.filter(name="timestamp")
def timestamp(obj: date):
    obj = obj or date.today()

    return mktime(obj.timetuple()) * 1000

@register.filter(name="render_code")
def render_code(text: str) -> str:
    output = ""
    count = 0

    for char in text:
        if char == '`':
            output = '%s<%skbd>' % (output, "/" if count % 2 != 0 else "")
            count += 1
        else:
            output = "".join([output, char])

    return output