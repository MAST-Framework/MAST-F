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
from django.db import models
from uuid import uuid4

from mastf.MASTF.utils.enum import ComponentCategory

from .mod_scan import Scanner, Scan
from .base import namespace, TimedModel

__all__ = ["Component", "IntentFilter"]

class IntentFilter(TimedModel):
    name = models.CharField(max_length=1024, blank=True)
    action = models.CharField(max_length=1024, blank=True)

class Component(TimedModel):
    cid = models.CharField(max_length=256, primary_key=True)
    scanner = models.ForeignKey(Scanner, on_delete=models.CASCADE)

    name = models.CharField(max_length=2048)
    is_exported = models.BooleanField(default=False)
    is_protected = models.BooleanField(default=True)
    is_launcher = models.BooleanField(default=False)
    is_main = models.BooleanField(default=False)

    category = models.CharField(
        blank=True, choices=ComponentCategory.choices, max_length=256
    )
    intent_filters = models.ManyToManyField(IntentFilter, related_name="components")

    @staticmethod
    def make_uuid(*args) -> str:
        return f"cpt_{uuid4()}"

    @staticmethod
    def stats(scan: Scan) -> list:  # type := list[namespace]
        values = []
        components = Component.objects.filter(scanner__scan=scan)

        categories = (
            components.values("category")
            .annotate(ccount=models.Count("category"))
            .order_by()
        )
        rel_count = 1 if len(components) == 0 else len(components)
        for element in categories:
            category = element["category"]
            data = namespace(count=element["ccount"], category=category)

            data.protected = len(
                components.filter(category=category, is_protected=True)
            )
            data.protected_rel = (data.protected / rel_count) * 100
            data.exported = len(components.filter(category=category, is_exported=True))
            data.exported_rel = (data.exported / rel_count) * 100
            values.append(data)
        return values
