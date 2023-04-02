from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib import messages

from mastf.MASTF import settings
from mastf.MASTF.mixins import ContextMixinBase
from mastf.MASTF.rest.views import rest_project
from mastf.MASTF.models import Project, Vulnerability, Namespace
from mastf.MASTF.serializers import ProjectSerializer
# This file stores additional views that will be used to
# display the web frontend

__all__ = [
    'DashboardView', 'ProjectsView'
]

class DashboardView(ContextMixinBase, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.prepare_context_data(self.request))

        context['selected'] = 'Home'
        return context


class ProjectsView(ContextMixinBase, TemplateView):
    template_name = 'dashboard/applications-and-projects.html'

    def post(self, request, *args, **kwargs):
        view = rest_project.ProjectCreationView.as_view()
        result = view(request)

        if result.status_code != 200:
            messages.error(request, "Could not create project!")

        return redirect('Projects')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        data = self.prepare_context_data(self.request, active='tabs-projects')
        stats = Project.stats(self.request.user)

        context.update(data)
        context.update(stats)
        context['columns'] = settings.PROJECTS_TABLE_COLUMNS

        vuln = Vulnerability.stats(self.request.user)
        context['vuln_count'] = vuln.count
        context['vuln_data'] = [
            self._get_vuln_context(vuln, "Critical", "pink"),
            self._get_vuln_context(vuln, "High", "red"),
            self._get_vuln_context(vuln, "Medium", "orange"),
            self._get_vuln_context(vuln, "Low", "yellow"),
            self._get_vuln_context(vuln, "Other", "secondary")
        ]

        return context

    def _get_vuln_context(self, stats: dict, name: str, bg: str) -> dict:
        field = f"{name.lower()}_vuln"
        return {
            'name': name,
            'color': f"bg-{bg}",
            'percent': stats[field] / stats.rel_count,
            'count': stats[field]
        }

    def _get_project_context(self, project: Project) -> Namespace:
        data = Namespace()
        data.update(ProjectSerializer(project).data)
        
        stats = Vulnerability.stats(project=project)
        
        return data






