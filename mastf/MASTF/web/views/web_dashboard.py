from django.shortcuts import redirect
from django.contrib import messages

from mastf.MASTF import settings
from mastf.MASTF.mixins import ContextMixinBase, VulnContextMixin, TemplateAPIView
from mastf.MASTF.rest.views import rest_project
from mastf.MASTF.models import (
    Project, Vulnerability, namespace, Scan, AbstractBaseFinding
)
from mastf.MASTF.serializers import ProjectSerializer, ScanSerializer
# This file stores additional views that will be used to
# display the web frontend

__all__ = [
    'DashboardView', 'ProjectsView', 'LicenseView', 'PluginsView'
]

class DashboardView(ContextMixinBase, TemplateAPIView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected'] = 'Home'

        messages.error(self.request, "Example error message", "Internal server Error")

        return context


class ProjectsView(VulnContextMixin, ContextMixinBase, TemplateAPIView):
    template_name = 'dashboard/bundles-and-projects.html'

    def post(self, request, *args, **kwargs):
        view = rest_project.ProjectCreationView.as_view()
        result = view(request)

        if result.status_code > 400:
            messages.error(request, "Could not create project!")

        return redirect('Projects')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active'] = 'tabs-projects'

        stats = Project.stats(self.request.user)
        context.update(stats)

        context['columns'] = settings.PROJECTS_TABLE_COLUMNS
        vuln = AbstractBaseFinding.stats(Vulnerability, member=self.request.user)
        self.apply_vuln_context(context, vuln)

        project_table_data = []
        for project_pk in stats['ids']:
            project_table_data.append(self._get_project_context(Project.objects.get(pk=project_pk)))

        context['project_table_data'] = project_table_data
        return context

    def _get_project_context(self, project: Project) -> namespace:
        data = namespace(project=project)
        data.update(AbstractBaseFinding.stats(Vulnerability, project=project))

        scan = Scan.objects.filter(project=project).order_by('start_date')
        data['scan'] = ScanSerializer(scan[0]).data if len(scan) > 0 else None
        return data


class LicenseView(ContextMixinBase, TemplateAPIView):
    template_name = 'license.html'


class PluginsView(ContextMixinBase, TemplateAPIView):
    template_name = 'dashboard/plugins.html'

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        context['active'] = 'tabs-permissions'
        return context
