from django.db import models

from mastf.MASTF.utils.enum import ComponentCategory

from .mod_scan import Scanner, Scan
from .base import namespace

__all__ = [
    'Component'
]

class Component(models.Model):
    cid = models.CharField(max_length=256, primary_key=True)
    scanner = models.ForeignKey(Scanner, on_delete=models.CASCADE)

    name = models.CharField(max_length=2048)
    is_exported = models.BooleanField(default=False)
    is_protected = models.BooleanField(default=False)
    category = models.CharField(null=True, choices=ComponentCategory.choices, max_length=256)

    @staticmethod
    def stats(scan: Scan) -> list: # type := list[namespace]
        values = []
        components = Component.objects.filter(scanner__scan=scan)

        categories = (components.values("category")
            .annotate(ccount=models.Count("category"))
            .order_by())
        rel_count = 1 if len(components) == 0 else len(components)
        for element in categories:
            category = element['category']
            data = namespace(count=element['ccount'], category=category)

            data.protected = len(components.filter(category=category, is_protected=True))
            data.protected_rel = (data.protected / rel_count) * 100
            data.exported = len(components.filter(category=category, is_exported=True))
            data.exported_rel = (data.exported / rel_count) * 100
            values.append(data)
        return values