"""MASTF URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, re_path

from mastf.MASTF import settings
from mastf.MASTF.views import dashboard, project, auth, scan
from mastf.MASTF.views.api import api_projects, api_auth, api_scans

urlpatterns = [
    # API
    re_path(r"^api/v1/newProject$", api_projects.api_new_project, name="(api)v1->newProject"),
    re_path(r"^api/v1/deleteProject$", api_projects.api_delete_project, name="(api)v1->deleteProject"),
    
    # User Management
    re_path(r"^api/v1/user/login$", api_auth.api_login_user, name="(api)v1->loginUser"),
    re_path(r"^api/v1/user/register$", api_auth.api_new_user, name="(api)v1->registerUser"),
    re_path(r"^api/v1/user/logout$", api_auth.api_logout_user, name="(api)v1->logoutUser"),
    
    re_path(r"^api/v1/scan/newScan$", api_scans.api_new_scan, name="(api)v1->newScan"),
    
]

if not settings.API_ONLY:
    
    urlpatterns.extend([
        path("", dashboard.index, name="Index"),
        path("applicationsAndProjects/", dashboard.applications_and_projects, name="applicationsAndProjects"),
        path("applicationsAndProjects/projects", dashboard.applications_and_projects, name="Projects"),
        path("applicationsAndProjects/applications", dashboard.applications_and_projects, name="Applications"),
        
        path("projects/<uuid:project_id>/overview", project.overview, name="ProjectOverview"),
        path("projects/<uuid:project_id>/", project.overview, name="ProjectOverviewDelegate"),
        path("projects/<uuid:project_id>/scanHistory", project.scan_history, name="ProjectScanHistory"),
        path("projects/<uuid:project_id>/scanners", project.scanners_results, name="ProjectScanners"),
        path("projects/<uuid:project_id>/scanners/<str:name>", scan.scan_results, name="ScannerResults"),
        path("projects/<uuid:project_id>/scanners/<str:name>/<str:extension>", scan.scan_results, name="ScannerResultsTab"),
        path("projects/<uuid:project_id>/packages", project.overview, name="ProjectPackages"),
        path("projects/<uuid:project_id>/settings", project.overview, name="ProjectSettings"),
        path("projects/newProject", project.new_project, name="newProject"),
        path("projects/deleteProject", project.delete_project, name="deleteProject"),
        
        path("scans/newScan", scan.new_scan, name="NewScan"),
        
        path("login", auth.signin_view, name="SignIn"),
        path("register", auth.signup_view, name="SignUp"),
        path("users/login", auth.login_user, name="LoginUser"),
        path("users/register", auth.register_user, name="RegisterUser"),
        path("users/logout", auth.logout_user, name="SignOut"),
        
        path("settings", dashboard.user_settings, name="UserSettings"),
        
        path("scans", dashboard.index, name="Scans"),
    ])
