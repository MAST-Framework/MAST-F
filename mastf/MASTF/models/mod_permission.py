from django.db import models

from .mod_finding import AbstractBaseFinding

__all__ = [
    'AppPermission', 'PermissionFinding'
]

class AppPermission(models.Model):
    permission_uuid = models.UUIDField(primary_key=True)
    identifier = models.CharField(max_length=256, null=False)
    name = models.CharField(max_length=256, null=True)
    # maybe add choices here
    protection_level = models.CharField(max_length=256, blank=True)
    dangerous = models.BooleanField(default=False)
    group = models.CharField(max_length=256, null=True)

    short_description = models.CharField(max_length=256, blank=True)
    description = models.TextField(blank=True)

    risk = models.TextField(blank=True)


class PermissionFinding(AbstractBaseFinding):
    permission = models.ForeignKey(AppPermission, null=True, on_delete=models.SET_NULL)
    
