from django import forms

from mastf.MASTF.settings import MASTF_PASSWD_MIN_LEN, MASTF_USERNAME_MIN_LEN

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


class ScanForm(forms.Form):
    project_uuid = forms.CharField(required=True, max_length=64)
    origin = forms.CharField(max_length=32, required=False)
    source = forms.CharField(max_length=256, required=True)
    scan_type = forms.CharField(max_length=256, required=True)
    start_date = forms.DateField(required=False)
    status = forms.CharField(max_length=256, required=False)
    file_url = forms.CharField(max_length=512, required=False)


class AbstractFindingForm(forms.Form):
    scan = forms.CharField(max_length=256, required=True)
    language = forms.CharField(max_length=256, required=False)
    severity = forms.CharField(max_length=32, required=True)
    source_file = forms.CharField(max_length=512, required=True)
    source_line = forms.CharField(max_length=512, required=False)
    scanner = forms.CharField(max_length=256, required=True)
    template = forms.CharField(max_length=256, required=True)
    
    class Meta:
        abstract = True


class FindingForm(AbstractFindingForm):
    is_custom = forms.BooleanField(required=False)


class VulnerabilityForm(AbstractFindingForm):
    state = forms.CharField(max_length=256, required=True)
    

class TeamForm(forms.Form):
    name = forms.CharField(max_length=256, required=True)
    owner_pk = forms.IntegerField(required=True)
    users = forms.CharField()
    