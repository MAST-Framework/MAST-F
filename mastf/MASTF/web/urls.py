from django.urls import path

from mastf.MASTF.web import views

urlpatterns = [
    path(r"", views.DashboardView.as_view(), name='Index'),
    path(r"web/dashboard", views.DashboardView.as_view(), name='Dashboard'),
    
    # URLs for the main navigation bar - Currently, there are only four options
    # (five with dashboard):
    path(r"web/projects/", views.ProjectsView.as_view(), name='Projects'),
    path(r"web/applications/", views.DashboardView.as_view(), name='Applications'),
    path(r"web/scans/", views.DashboardView.as_view(), name='Scans'),
    path(r"web/plug-ins/", views.DashboardView.as_view(), name='Plug-Ins'),
    
    # Top navigation bar links, that can be used to view the user's profile, 
    # logout or to navigate to the global settings.
    path(r"web/settings/", views.DashboardView.as_view(), name='Settings'),
    path(r"web/logout", views.LogoutView.as_view(), name='Settings'),
    
    # Both views will be treated special as they don't need any authorization.
    # Note that each view implements GET requests to render the HTML page and
    # uses POST to perform an action.
    path(r"web/login", views.LoginView.as_view(), name='User-Login'),
    path(r"web/register", views.RegstrationView.as_view(), name='User-Registration'),
    
]
