from django import forms
from django.contrib.auth.models import User

from mastf.MASTF.settings import MASTF_PASSWD_MIN_LEN, MASTF_USERNAME_MIN_LEN

__all__ = [
    'ModelField', 'RegistrationForm', 'ProjectCreationForm', 
    'AppPermissionForm', 'TeamForm', 
]

class ModelField(forms.CharField):
    
    def __init__(self, model, field_name='pk', **kwargs) -> None:
        super().__init__(**kwargs)
        self.model = model
        self.field_name = field_name
    
    def to_python(self, value: str) -> object:
        return self.model.objects.get(**{self.field_name: value})

    def validate(self, value: object) -> None:
        query = {self.field_name: value}
        if not self.model.objects.filter(**query).exists():
            raise forms.ValidationError(
                "This field must be a reference to an existing model", code="required")


class RegistrationForm(forms.Form):
    """Simple form used to register new users"""

    username = forms.CharField(
        max_length=256, min_length=MASTF_USERNAME_MIN_LEN,
        required=True)
    """The username which has to be unique"""

    password = forms.CharField(
        max_length=256, min_length=MASTF_PASSWD_MIN_LEN,
        required=True
    )
    """The minimum password length will be defined by ``MASTF_PASSWD_MIN_LEN``."""


class ProjectCreationForm(forms.Form):
    """Simple form to create new projects"""
    
    name = forms.CharField(max_length=256, required=True)
    tags = forms.CharField(max_length=4096, required=False)
    visibility = forms.CharField(max_length=32, required=True)
    risk_level = forms.CharField(max_length=16, required=True)
    inspection_type = forms.CharField(max_length=32, required=True)
    team_name = forms.CharField(max_length=256, required=False)


class AppPermissionForm(forms.Form):
    """Form used to create and update app permissions"""
    identifier = forms.CharField(max_length=256, required=True)
    name = forms.CharField(max_length=256, required=True)
    protection_level = forms.CharField(max_length=256, required=True)
    dangerous = forms.BooleanField(required=False, initial=False)
    group = forms.CharField(max_length=256, required=True)
    
    short_description = forms.CharField(max_length=256, required=True)
    description = forms.CharField(required=False)
    risk = forms.CharField(required=False) 


class TeamForm(forms.Form):
    name = forms.CharField(max_length=256, required=True)
    owner = ModelField(User, field_name='username', max_length=256)
    users = forms.CharField()
    
