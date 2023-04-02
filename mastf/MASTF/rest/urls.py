from django.urls import path

from mastf.MASTF.rest import views

urlpatterns = [
    path(r"api/v1/user/<int:pk>", views.UserView.as_view()),
    
    path(r"api/v1/login", views.LoginView.as_view()),
    path(r"api/v1/logout", views.LogoutView.as_view()),
    path(r"api/v1/register", views.RegistrationView.as_view()),
    
    path(r"api/v1/project/<uuid:project_uuid>", views.ProjectView.as_view()),
    path(r"api/v1/project/create", views.ProjectCreationView.as_view()),
    path(r"api/v1/project/all", views.ProjectListView.as_view()),
    
    # Note that we're using the custom converter defined in
    # mastf/MASTF/converters.py
    path(r"api/v1/finding/template/all", views.FindingTemplateListView.as_view()),
    path(r"api/v1/finding/template/create", views.FindingTemplateCreationView.as_view()),
    path(r"api/v1/finding/template/<ftid:template_id>", views.FindingTemplateView.as_view()),
    
    path(r"api/v1/app-permission/all", views.AppPermissionListView.as_view()),
    path(r"api/v1/app-permission/create", views.AppPermissionCreationView.as_view()),
    path(r"api/v1/app-permission/<uuid:permission_uuid>", views.AppPermissionView.as_view()),
    
    path(r"api/v1/scan/all", views.ScanListView.as_view()),
    path(r"api/v1/scan/create", views.ScanCreationView.as_view()),
    path(r"api/v1/scan/<uuid:scan_uuid>", views.ScanView.as_view()),
    path(r"api/v1/scan/<uuid:scan_uuid>/<str:name>/<str:extension>", views.ScannerView.as_view()),
    
    # Code methods for findings and vulerabilities
    path(r"api/v1/code/<sfid:finding_id>", views.FindingCodeView.as_view()),
    path(r"api/v1/code/<svid:finding_id>", views.FindingCodeView.as_view()),
    
]


