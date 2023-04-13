from django.urls import path, include

from mastf.MASTF.rest import views

urlpatterns = [
    path(r"user/<int:pk>", views.UserView.as_view()),

    path(r"login", views.LoginView.as_view()),
    path(r"logout", views.LogoutView.as_view()),
    path(r"register", views.RegistrationView.as_view()),

    path(r"project/", include([
        path(r"<uuid:project_uuid>", views.ProjectView.as_view()),
        path(r"create", views.ProjectCreationView.as_view()),
        path(r"all", views.ProjectListView.as_view()),

        path(r"<uuid:project_uuid>/chart/<str:name>", views.ProjectChartView.as_view())
    ])),

    # Note that we're using the custom converter defined in
    # mastf/MASTF/converters.py
    path(r"finding/", include([
        # REVISIT: Potential information leakage when listing vulnerabilities 
        # from other projects
        path(r"all", views.FindingListView.as_view()),
        path(r"create", views.FindingCreationView.as_view()),
        path(r"<sfid:finding_id>", views.FindingView.as_view()),
        
        path(r"vulnerability/all", views.VulnerabilityListView.as_view()),
        path(r"vulnerability/create", views.VulnerabilityCreationView.as_view()),
        path(r"vulnerability/<svid:finding_id>", views.VulnerabilityView.as_view()),
        
        path(r"template/all", views.FindingTemplateListView.as_view()),
        path(r"template/create", views.FindingTemplateCreationView.as_view()),
        path(r"template/<ftid:template_id>", views.FindingTemplateView.as_view()),
    ])),
    
    path(r"app-permission/all", views.AppPermissionListView.as_view()),
    path(r"app-permission/create", views.AppPermissionCreationView.as_view()),
    path(r"app-permission/<uuid:permission_uuid>", views.AppPermissionView.as_view()),

    path(r"scan/", include([
        path(r"all", views.ScanListView.as_view()),
        path(r"create", views.ScanCreationView.as_view()),
        path(r"<uuid:scan_uuid>", views.ScanView.as_view()),
        path(r"<uuid:scan_uuid>/<str:name>/<str:extension>", views.ScannerView.as_view()),
        path(r"task/<uuid:task_uuid>", views.ScanTaskView.as_view()),
    ])),
    

    # Code methods for findings and vulerabilities
    path(r"code/<sfid:finding_id>", views.FindingCodeView.as_view()),
    path(r"code/<svid:finding_id>", views.VulnerabilityCodeView.as_view()),

    path(r"team/", include([
        path("<int:pk>", views.TeamView.as_view()),
        path("all", views.TeamListView.as_view()),
        path("create", views.TeamCreationView.as_view()),
    ])),
    
    path(r"package/", include([
        # We have to use 'pk' here as the name, because we haven't specified
        # a custom lookup field in the PackageView class
        path(r"<uuid:pk>", views.PackageView.as_view()),
        path(r"all", views.PackageListView.as_view()),
        path(r"create", views.PackageCreationView.as_view()),
        
        path(r"vulnerability/", include([
            path(r"<uuid:pk>", views.PackageVulnerabilityView.as_view()),
            path(r"all", views.PackageVulnerabilityListView.as_view()),
            path(r"create", views.PackageVulnerabilityCreationView.as_view()),
        ]))
    ])),
    
    
]


