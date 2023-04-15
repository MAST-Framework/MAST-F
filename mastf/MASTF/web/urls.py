from django.urls import path, include

from mastf.MASTF.web import views

urlpatterns = [
    path(r"", views.DashboardView.as_view(), name='Index'),
    path(r"dashboard", views.DashboardView.as_view(), name='Dashboard'),
    path(r"license", views.LicenseView.as_view(), name='License'),

    # URLs for the main navigation bar - Currently, there are only four options
    # (five with dashboard):
    path(r"projects/", views.ProjectsView.as_view(), name='Projects'),
    path(r"bundles/", views.DashboardView.as_view(), name='Bundles'),
    path(r"scans/", views.DashboardView.as_view(), name='Scans'),
    path(r"plug-ins/", views.PluginsView.as_view(), name='Plug-Ins'),

    # Top navigation bar links, that can be used to view the user's profile,
    # logout or to navigate to the global settings.
    path(r"settings/", views.DashboardView.as_view(), name='Settings'),
    path(r"logout", views.LogoutView.as_view(), name='Settings'),

    # Both views will be treated special as they don't need any authorization.
    # Note that each view implements GET requests to render the HTML page and
    # uses POST to perform an action.
    path(r"login", views.LoginView.as_view(), name='User-Login'),
    path(r"register", views.RegstrationView.as_view(), name='User-Registration'),


    path(r"projects/<uuid:project_uuid>/", include([
        path(r"overview", views.UserProjectDetailsView.as_view(), name='Project-Overview'),
        path(r"scan-history", views.UserProjectScanHistoryView.as_view(), name='Project-Scan-History'),
        path(r"scanners", views.UserScannersView.as_view(), name='Project-Scanners'),
        path(r"packages", views.UserProjectPackagesView.as_view(), name='Project-Packages'),
        path(r"explorer", views.UserProjectDetailsView.as_view(), name='Project-Explorer'),
        path(r"export", views.UserProjectDetailsView.as_view(), name='Project-Export'),
        path(r"settings", views.UserProjectDetailsView.as_view(), name='Project-Settings'),

    ])),

    path(r"results/<uuid:project_uuid>/<str:name>/", include([
        path(r"", views.ScanIndexView.as_view(), name='Scan-Index'),
        # We're placing this url in a list as there may be more urls within
        # a scanner in the future. The initial page won't show any file
        # related information, but can be used to display error messages
        path(r"<md5:file_md5>/", views.ScannerResultsView.as_view(), name='Scan-Results-Index'),
        path(r"<md5:file_md5>/<str:extension>", views.ScannerResultsView.as_view(), name='Scan-Results'),
    ])),

    path(r"details/<str:platform>/<str:name>", views.DetailsView.as_view(), name="Details"),

]
