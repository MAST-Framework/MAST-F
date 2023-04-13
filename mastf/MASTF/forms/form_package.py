from django import forms

from mastf.MASTF.models import Package

from .base import ModelField

__all__ = [
    'PackageForm', 'PackageVulnerabilityForm'
]
  
class PackageForm(forms.Form):
    name = forms.CharField(max_length=512, required=True)
    artifact_id = forms.CharField(max_length=512, required=True)
    group_id = forms.CharField(max_length=512, required=True)
    type = forms.CharField(max_length=256, required=True)
    platform = forms.CharField(max_length=256, required=True)


class PackageVulnerabilityForm(forms.Form):
    cve_id = forms.CharField(max_length=256, required=True)
    package = ModelField(Package, max_length=72, required=True)
    version = forms.CharField(max_length=512, required=True)
    