from django import forms

from mastf.MASTF.models import Host, Scan, Snippet

from .base import ModelField, ManyToManyField

__all__ = [
    'ConnectionForm',
    'CipherSuiteForm',
    'TLSForm',
    'DataCollectionGroupForm',
    'HostForm',
]

class ConnectionForm(forms.Form):
    host = ModelField(Host, max_length=256, required=True)
    ip = forms.CharField(max_length=32, required=True)
    port = forms.IntegerField(max_value=65535, min_value=0, required=True)
    protocol = forms.CharField(max_length=256, required=False)
    country = forms.CharField(max_length=256, required=False)
    longitude = forms.FloatField(required=False)
    langitude = forms.FloatField(required=False)

class CipherSuiteForm(forms.Form):
    hosts = ManyToManyField(Host, max_length=256, required=False)
    name = forms.CharField(max_length=256, required=True)
    recommended = forms.BooleanField(required=False)

class TLSForm(forms.Form):
    hosts = ManyToManyField(Host, max_length=256, required=False)
    name = forms.CharField(max_length=256, required=True)
    recommended = forms.BooleanField(required=False)

class DataCollectionGroupForm(forms.Form):
    hosts = ManyToManyField(Host, max_length=256, required=False)
    group = forms.CharField(max_length=256, required=True)
    protection_level = forms.CharField(max_length=256, required=False)

class HostForm(forms.Form):
    scan = ModelField(Scan, required=True)
    classification = forms.CharField(max_length=256, required=False)
    snippet = ModelField(Snippet, required=False)
    url = forms.URLField(max_length=2048, required=True)
    domain = forms.CharField(max_length=256, required=True)








