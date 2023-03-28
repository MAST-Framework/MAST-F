from django import forms


class ProjectForm(forms.Form):
    
    project_name = forms.CharField(max_length=256)
    """The name of the project."""
    
    report_type = forms.CharField(max_length=32)
    tags = forms.CharField(max_length=2048, required=False)
    visibility = forms.CharField(max_length=256)
    
    
class ProjectDeleteForm(forms.Form):
    
    project_uuid = forms.UUIDField(required=True)
    """THe project's uuid"""
    

class RegisterUserForm(forms.Form):
    
    username = forms.CharField(max_length=256)
    password = forms.CharField(max_length=256, min_length=12)
    

class ProjectScanForm(forms.Form):
    
    project_id = forms.UUIDField(required=True)
    date = forms.DateField(input_formats="d m Y", required=False)
    source = forms.CharField(max_length=32)
    file_url = forms.CharField(max_length=2048, required=False)
    file = forms.FileField(required=False)

class ScanGetResultsForm(forms.Form):
    
    project_id = forms.UUIDField(required=True)
    scanner_name = forms.CharField(max_length=32, required=True)
    extension = forms.CharField(max_length=256, required=True)
