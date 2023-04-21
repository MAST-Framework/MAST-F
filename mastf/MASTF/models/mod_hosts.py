from django.db import models

__all__ = ["Hosts"]

#Model to save hosts for Plugin Page
class Hosts(models.Model):
    host_uuid = models.UUIDField(primary_key=True)
    domain_name = models.CharField(max_length=256, null=False)
    ip_adress = models.CharField(max_length=32, null=True)
    owner = models.CharField(max_length=255, null=True)
    description = models.TextField(null=False)