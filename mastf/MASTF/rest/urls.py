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
        path(r"dependencies", views.DependencyListView.as_view()),

        path(r"<uuid:project_uuid>/chart/<str:name>", views.ProjectChartView.as_view()),
    ])),

    # Note that we're using the custom converter defined in
    # mastf/MASTF/converters.py
    path(r"finding/", include([
        path(r"create", views.FindingCreationView.as_view()),
        path(r"<findingid:finding_id>", views.FindingView.as_view()),

        path(r"vulnerability/create", views.VulnerabilityCreationView.as_view()),
        path(r"vulnerability/<vulnerabilityid:finding_id>", views.VulnerabilityView.as_view()),

        path(r"template/all", views.FindingTemplateListView.as_view()),
        path(r"template/create", views.FindingTemplateCreationView.as_view()),
        path(r"template/<findingtemplateid:template_id>", views.FindingTemplateView.as_view()),
    ])),

    path(r"app-permission/all", views.AppPermissionListView.as_view(), name="AppPermissionListView"),
    path(r"app-permission/create", views.AppPermissionCreationView.as_view(), name="AppPermissionCreate"),
    path(r"app-permission/<uuid:permission_uuid>", views.AppPermissionView.as_view(), name="AppPermissionView"),

    path(r"scan/", include([
        path(r"all", views.ScanListView.as_view()),
        path(r"create", views.ScanCreationView.as_view()),
        path(r"<uuid:scan_uuid>/", include([
            path(r"", views.ScanView.as_view()),

            # Note that all path elements below will return results according
            # to the selected scan - mapping the results of all scanners
            # together. To get accurate results for each scanner, you should
            # address the extension of each scanner directly.
            path(r"filetree", views.FiletreeView.as_view()),
            path(r"findings",  views.FindingListView.as_view()),
            path(r"vulnerabilities", views.VulnerabilityListView.as_view()),
            path(r"permissions", views.AppPermissionListView.as_view()),
            path(r"hosts", views.HostListView.as_view()),
            path(r"components", views.ComponentListView.as_view()),

            path(r"<str:name>/<str:extension>", views.ScannerView.as_view()),
        ])),

        path(r"task/<uuid:task_uuid>", views.ScanTaskView.as_view()),
    ])),


    # Code methods for findings and vulerabilities
    path(r"code/<findingid:finding_id>", views.FindingCodeView.as_view()),
    path(r"code/<vulnerabilityid:finding_id>", views.VulnerabilityCodeView.as_view()),
    path(r"files/<md5:internal_name>/", views.FileCodeView.as_view()),

    path(r"team/", include([
        path("<int:pk>", views.TeamView.as_view()),
        path("all", views.TeamListView.as_view()),
        path("create", views.TeamCreationView.as_view()),
    ])),

    path(r"package/", include([
        # We have to use 'pk' here as the name, because we haven't specified
        # a custom lookup field in the PackageView class
        path(r"<uuid:pk>", views.PackageView.as_view(), name="PackageView"),
        path(r"all", views.PackageListView.as_view(), name="PackageListView"),
        path(r"create", views.PackageCreationView.as_view(), name="PackageCreationView"),

        path(r"vulnerability/", include([
            path(r"<uuid:pk>", views.PackageVulnerabilityView.as_view()),
            path(r"all", views.PackageVulnerabilityListView.as_view()),
            path(r"create", views.PackageVulnerabilityCreationView.as_view()),
        ]))
    ])),

    path(r"dependency/", include([
        path(r"create", views.DependencyCreationView.as_view()),
        path(r"<str:pk>", views.DependencyView.as_view()),
    ])),

    path(r"host/", include([
        path(r"create", views.HostCreationView.as_view()),
        path(r"<hostid:pk>/", include([
            path(r"", views.HostView.as_view()),

            path(r"tls", views.TLSListView.as_view()),
            path(r"ciphersuites", views.CipherSuiteListView.as_view()),
            path(r"datacollection", views.DataCollectionGroupListView.as_view()),
        ])),

        path(r"template/", include([
            # The following lines have been moved from the root path to this sub-path:
            # path(r"hosts/create", views.HostCreationView.as_view(), name="HostCreate"),
            # path(r"hosts/all", views.HostsListView.as_view(), name="HostListView"),
            # path(r"hosts/<uuid:host_uuid>", views.HostView.as_view(), name="HostView"),

            path(r"create", views.HostTemplateCreationView.as_view(), name="HostCreate"),
            path(r"all", views.HostTemplateListView.as_view(), name="HostListView"),
            path(r"<uuid:pk>", views.HostTemplateView.as_view(), name="HostView"),
        ])),

        path(r"tls/", include([
            path(r"create", views.TLSCreationView.as_view()),
            path(r"<uuid:pk>", views.TLSView.as_view()),
        ])),

        path(r"cipher/", include([
            path(r"create", views.TLSCreationView.as_view()),
            path(r"<uuid:pk>", views.TLSView.as_view()),
        ])),

        path(r"datacoll/", include([
            path(r"create", views.DataCollectionGroupCreationView.as_view()),
            path(r"<uuid:pk>", views.DataCollectionGroupView.as_view()),
        ]))
    ])),

    path(r"component/", include([
        path(r"create", views.ComponentCreationView.as_view()),
        path(r"<componentid:pk>", views.ComponentView.as_view()),
    ])),

]


