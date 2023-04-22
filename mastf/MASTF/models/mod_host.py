from django.db import models

from mastf.MASTF.utils.enum import HostType, DataProtectionLevel
from mastf.MASTF.models import Snippet, Scan, Scanner

class TLS(models.Model):
    tls_uuid = models.UUIDField(primary_key=True)
    version = models.CharField(max_length=256, null=True)
    recommended = models.BooleanField(default=False)

class CipherSuite(models.Model):
    cipher_uuid = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=256, blank=True)
    recommended = models.BooleanField(default=False)

class DataCollectionGroup(models.Model):
    dc_uuid = models.UUIDField(primary_key=True)
    group = models.CharField(max_length=256, null=False)
    protection_level = models.CharField(default=DataProtectionLevel.PUBLIC, choices=DataProtectionLevel.choices, max_length=256)


class Host(models.Model):
    host_id = models.CharField(max_length=256, primary_key=True)
    scan = models.ForeignKey(Scan, on_delete=models.CASCADE)
    scanner = models.ForeignKey(Scanner, on_delete=models.CASCADE, null=True)

    classification = models.CharField(default=HostType.NOT_SET, choices=HostType.choices, max_length=256)
    snippet = models.ForeignKey(Snippet, on_delete=models.SET_NULL, null=True)
    url = models.CharField(max_length=2048, null=True, blank=True)
    domain = models.CharField(max_length=2048, null=True)
    ip = models.CharField(max_length=32, null=True)
    port = models.IntegerField(default=0)
    protocol = models.CharField(max_length=256, null=True)
    country = models.CharField(max_length=256, null=True)
    longitude = models.FloatField(null=True)
    latitude = models.FloatField(null=True)

    tlsversions = models.ManyToManyField(TLS, related_name='hosts')
    suites = models.ManyToManyField(CipherSuite, related_name='hosts')
    collected_data = models.ManyToManyField(DataCollectionGroup, related_name='hosts')

