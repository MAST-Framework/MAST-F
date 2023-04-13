from django import forms

from mastf.MASTF.models import Scan, FindingTemplate, Scanner
from .base import ModelField

__all__ = [
    'FindingTemplateForm', 'AbstractFindingForm', 'FindingForm', 
    'VulnerabilityForm'
]

class FindingTemplateForm(forms.Form):
    """Form used to validate update requests of finding templates.
    
    Note that this form is also used when creating new instances
    of finding templates and registering them in the database.
    
    All attributes must be declared as not required to enable performing
    single attribute updates.
    """
    
    title = forms.CharField(max_length=256, required=False)
    severity = forms.CharField(max_length=256, required=False)
    # The next two fields won't get a length maximum
    description = forms.CharField(required=False)
    risk = forms.CharField(required=False)
    mitigation = forms.CharField(required=False)


class AbstractFindingForm(forms.Form):
    scan = ModelField(Scan, max_length=256, required=True)
    language = forms.CharField(max_length=256, required=False)
    severity = forms.CharField(max_length=32, required=True)
    source_file = forms.CharField(max_length=512, required=True)
    source_line = forms.CharField(max_length=512, required=False)
    scanner = ModelField(Scanner, max_length=256, required=True)
    template = ModelField(FindingTemplate, max_length=256, required=True)
    
    class Meta:
        abstract = True


class FindingForm(AbstractFindingForm):
    is_custom = forms.BooleanField(required=False)


class VulnerabilityForm(AbstractFindingForm):
    state = forms.CharField(max_length=256, required=True)
    