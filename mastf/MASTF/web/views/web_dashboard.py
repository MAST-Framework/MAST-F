from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib import messages

from mastf.MASTF import settings
from mastf.MASTF.mixins import ContextMixinBase, VulnContextMixin
from mastf.MASTF.rest.views import rest_project
from mastf.MASTF.models import (
    Project, Vulnerability, Namespace, Scan
)
from mastf.MASTF.serializers import ProjectSerializer, ScanSerializer
# This file stores additional views that will be used to
# display the web frontend

__all__ = [
    'DashboardView', 'ProjectsView', 'LicenseView', 'PluginsView'
]

class DashboardView(ContextMixinBase):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected'] = 'Home'
        
        messages.error(self.request, "Some error message", "Internal server Error")
        
        return context


class ProjectsView(VulnContextMixin, ContextMixinBase):
    template_name = 'dashboard/applications-and-projects.html'

    def post(self, request, *args, **kwargs):
        view = rest_project.ProjectCreationView.as_view()
        result = view(request)

        if result.status_code != 200:
            messages.error(request, "Could not create project!")

        return redirect('Projects')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active'] = 'tabs-projects'
        
        stats = Project.stats(self.request.user)
        context.update(stats)
        
        context['columns'] = settings.PROJECTS_TABLE_COLUMNS
        vuln = Vulnerability.stats(self.request.user)
        self.apply_vuln_context(context, vuln)
        
        project_table_data = []
        for project in Project.objects.filter(owner=self.request.user):
            project_table_data.append(self._get_project_context(project))
        
        context['project_table_data'] = project_table_data
        return context

    def _get_project_context(self, project: Project) -> Namespace:
        data = Namespace()
        data.update(ProjectSerializer(project).data)
        data.update(Vulnerability.stats(project=project))
        
        scan = Scan.objects.filter(project=project).order_by('start_date')
        data['scan'] = ScanSerializer(scan[0]).data if len(scan) > 0 else None

        return data


class LicenseView(ContextMixinBase):
    template_name = 'license.html'


class PluginsView(ContextMixinBase):
    template_name = 'dashboard/plugins.html'

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        context['active'] = 'tabs-permissions'
        return context