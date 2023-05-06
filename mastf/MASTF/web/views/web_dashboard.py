from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import models

from mastf.MASTF import settings
from mastf.MASTF.scanners.plugin import ScannerPlugin
from mastf.MASTF.rest.views import rest_project, rest_scan
from mastf.MASTF.rest.permissions import IsExternal
from mastf.MASTF.utils.enum import Visibility
from mastf.MASTF.models import (
    Project,
    Vulnerability,
    namespace,
    Scan,
    AbstractBaseFinding,
    Finding,
    Bundle,
    Team,
)
from mastf.MASTF.serializers import ScanSerializer

from mastf.MASTF.utils.enum import Platform, PackageType, ProtectionLevel
from mastf.MASTF.mixins import (
    ContextMixinBase,
    VulnContextMixin,
    TemplateAPIView,
    TopVulnerableProjectsMixin,
    ScanTimelineMixin
)
# This file stores additional views that will be used to
# display the web frontend

__all__ = [
    "DashboardView",
    "ProjectsView",
    "LicenseView",
    "PluginsView",
    "BundlesView",
    "ScansView",
]


class DashboardView(ContextMixinBase, TopVulnerableProjectsMixin,
                    VulnContextMixin, ScanTimelineMixin, TemplateAPIView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["selected"] = "Home"
        projects = Project.get_by_user(self.request.user)

        context.update(self.get_top_vulnerable_projects(projects))

        context["vuln_timeline"] = self.get_timeline(Vulnerability, projects)
        context["finding_timeline"] = self.get_timeline(Finding, projects)
        context["scan_timeline"] = self.get_scan_timeline(projects)

        bundles = Bundle.get_by_owner(self.request.user)
        context["bundle_count"] = len(bundles)
        context["inherited_bundle_count"] = len(bundles.filter(~models.Q(owner=self.request.user)))

        context["project_count"] = len(projects)
        context["public_project_count"] = len(projects.filter(visibility=Visibility.PUBLIC))

        scans = Scan.objects.filter(project__in=projects)
        context["scan_count"] = len(scans)
        context["active_scan_count"] = len(scans.filter(is_active=True))

        teams = Team.get_by_owner(self.request.user)
        context["team_count"] = len(teams)
        context["public_team_count"] = len(teams.filter(visibility=Visibility.PUBLIC))
        return context

    def get_timeline(self, model, projects) -> namespace:
        data = namespace()
        queryset = model.objects.filter(scan__project__in=projects)

        data.objects = (queryset
            .values("discovery_date")
            .annotate(total=models.Count('discovery_date'))
        )
        data.count = len(queryset)
        return data


class ProjectsView(VulnContextMixin, ContextMixinBase, TemplateAPIView):
    template_name = "dashboard/projects.html"

    def post(self, request, *args, **kwargs):
        view = rest_project.ProjectCreationView.as_view()
        result = view(request)

        if result.status_code > 400:
            messages.error(request, "Could not create project!")

        return redirect("Projects")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active"] = context["selected"] = "tabs-projects"

        stats = Project.stats(self.request.user)
        context.update(stats)

        context["columns"] = settings.PROJECTS_TABLE_COLUMNS
        vuln = AbstractBaseFinding.stats(Vulnerability, member=self.request.user)
        self.apply_vuln_context(context, vuln)

        project_table_data = []
        for project_pk in stats["ids"]:
            project_table_data.append(
                self._get_project_context(Project.objects.get(pk=project_pk))
            )

        context["project_table_data"] = project_table_data
        return context

    def _get_project_context(self, project: Project) -> namespace:
        data = namespace(project=project)
        data.update(AbstractBaseFinding.stats(Vulnerability, project=project))

        scan = Scan.objects.filter(project=project).order_by("start_date")
        data["scan"] = ScanSerializer(scan[0]).data if len(scan) > 0 else None
        return data


class BundlesView(VulnContextMixin, ContextMixinBase, TemplateAPIView):
    template_name = "dashboard/bundles.html"

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        context["active"] = context["selected"] = "tabs-bundles"
        stats = Bundle.stats(self.request.user)
        context.update(stats)

        level_data = self._get_level_data()
        self.apply_vuln_context(context, level_data)

        bundle_table_data = []
        for bundle_pk in stats["ids"]:
            bundle_table_data.append(
                self._get_bundle_context(Bundle.objects.get(pk=bundle_pk))
            )

        context["bundle_table_data"] = bundle_table_data
        return context

    def _get_level_data(self) -> dict:
        bundles = Bundle.get_by_owner(self.request.user)
        levels = (
            bundles.values("projects__risk_level")
            .annotate(count=models.Count("projects__risk_level"))
            .order_by()
        )

        level_data = namespace(count=0)
        for data in levels:
            level_data.count = level_data.count + data["count"]
            level_data[str(data["projects__risk_level"]).lower()] = data["count"]
        return level_data

    def _get_bundle_context(self, bundle: Bundle) -> namespace:
        data = namespace(bundle=bundle)
        data.update(AbstractBaseFinding.stats(Vulnerability, bundle=bundle))
        return data


class LicenseView(ContextMixinBase, TemplateAPIView):
    template_name = "license.html"


class PluginsView(ContextMixinBase, TemplateAPIView):
    template_name = "plugins/plugins-base.html"
    permission_classes = [
        # External users should not be able to query data from internal
        # configured templates
        ~IsExternal
    ]

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        if "subpage" in self.request.GET:
            subpage = self.request.GET["subpage"]
            if subpage == "packages":
                context["active"] = "tabs-packages"
                context["platforms"] = list(Platform)
                context["type"] = list(PackageType)
            elif subpage == "hosts":
                context["active"] = "tabs-hosts"
            else:
                context["active"] = "tabs-permissions"
                context["protection_levels"] = list(ProtectionLevel)
        else:
            context["active"] = "tabs-permissions"
            context["protection_levels"] = list(ProtectionLevel)

        page = self.request.GET.get("subpage", None)

        context["active"] = "tabs-permissions"
        self.template_name = "plugins/plugin-permissions.html"
        if page in ("packages", "hosts", "permissions"):
            context["active"] = f"tabs-{page}"
            self.template_name = f"plugins/plugin-{page}.html"

        context["selected"] = "tabs-plugins"
        return context


class ScansView(ContextMixinBase, ScanTimelineMixin, TemplateAPIView):
    template_name = "dashboard/scans.html"

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        projects = Project.get_by_user(self.request.user)

        context["scan_table_data"] = self.get_scan_timeline(projects)
        context["scanners"] = ScannerPlugin.all()
        context["available"] = projects
        context["selected"] = "tabs-scans"
        return context

    def post(self, request, *args, **kwargs):
        view = rest_scan.MultipleScanCreationView.as_view()
        view(request)
        return redirect("Scans", **self.kwargs)
