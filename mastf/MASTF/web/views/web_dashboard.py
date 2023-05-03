from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import models
from django.views import View

from mastf.MASTF import settings
from mastf.MASTF.scanners.plugin import ScannerPlugin
from mastf.MASTF.mixins import ContextMixinBase, VulnContextMixin, TemplateAPIView
from mastf.MASTF.rest.views import rest_project, rest_scan
from mastf.MASTF.utils.enum import Visibility, Role
from mastf.MASTF.models import (
    Project,
    Vulnerability,
    namespace,
    Scan,
    AbstractBaseFinding,
    Finding,
    Bundle,
    Environment,
    Account
)
from mastf.MASTF.forms import SetupForm
from mastf.MASTF.serializers import ScanSerializer
from mastf.MASTF.permissions import (
    CanEditUser,
    CanEditAccount,
    CanViewAccount,
    CanCreateUser,
    CanDeleteUser,
)

from mastf.MASTF.utils.enum import Platform, PackageType, ProtectionLevel

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


class DashboardView(ContextMixinBase, TemplateAPIView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["selected"] = "Home"
        return context


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
        context["active"] = "tabs-projects"

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
        context["active"] = "tabs-bundles"
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
    template_name = "dashboard/plugins.html"

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
        if page in ("packages", "hosts", "permissions"):
            context["active"] = f"tabs-{page}"
        else:
            context["active"] = "tabs-permissions"
        return context


class ScansView(ContextMixinBase, TemplateAPIView):
    template_name = "dashboard/scans.html"

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)

        visibility_level = [str(x).upper() for x in Visibility]
        for name in visibility_level:
            if self.request.GET.get(name.lower(), "true").lower() != "true":
                visibility_level.remove(name)

        projects = Project.get_by_user(self.request.user)
        scans = (
            Scan.objects.filter(project__visibility__in=visibility_level)
            .filter(project__in=projects)
            .order_by("start_date")
        )

        scan_table_data = []
        for scan in scans:
            vuln_stats = AbstractBaseFinding.stats(Vulnerability, scan=scan)
            finding_stats = AbstractBaseFinding.stats(Finding, scan=scan)

            data = namespace(scan=scan)
            data.findings = vuln_stats.count + finding_stats.count
            data.high_risks = vuln_stats.high + finding_stats.high
            data.medium_risks = vuln_stats.medium + finding_stats.medium
            data.low_risks = vuln_stats.low + finding_stats.low
            scan_table_data.append(data)

        context["scan_table_data"] = scan_table_data
        context["scanners"] = ScannerPlugin.all()
        context["available"] = projects
        return context

    def post(self, request, *args, **kwargs):
        view = rest_scan.MultipleScanCreationView.as_view()
        view(request)
        return redirect("Scans", **self.kwargs)
