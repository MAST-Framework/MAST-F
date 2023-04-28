from django import forms

from mastf.MASTF.models import Project
from .base import ModelField, ManyToManyField

__all__ = [
    'ScanForm'
]

class ScanForm(forms.Form):
    project = ModelField(Project, required=False, max_length=64)
    origin = forms.CharField(max_length=32, required=False)
    source = forms.CharField(max_length=256, required=True)
    scan_type = forms.CharField(max_length=256, required=True)
    start_date = forms.DateField(required=False)
    status = forms.CharField(max_length=256, required=False)
    file_url = forms.CharField(max_length=512, required=False)

    projects = ManyToManyField(Project, required=False)

