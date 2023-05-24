# This file is part of MAST-F's Frontend API
# Copyright (C) 2023  MatrixEditor
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
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
    ScanTimelineMixin,
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


class DashboardView(
    ContextMixinBase,
    TopVulnerableProjectsMixin,
    VulnContextMixin,
    ScanTimelineMixin,
    TemplateAPIView,
):
    """
    View class for the dashboard page.

    This class represents the view for the dashboard page, which provides various
    statistics and information about projects, vulnerabilities, scans, bundles,
    and teams. It inherits from several mixins to incorporate different functionalities
    into the view.

    :ivar template_name: The name of the HTML template used for rendering the dashboard page.
    :vartype template_name: str
    """

    template_name = "index.html"

    def get_context_data(self, **kwargs):
        """
        Retrieve the context data for rendering the dashboard page.

        This method retrieves and prepares the necessary data to be used in the template
        rendering process for the dashboard page. It includes information about the user's
        projects, vulnerable projects, timelines, bundles, project counts, scan counts,
        team counts, and more.

        :param kwargs: Additional keyword arguments.
        :return: The context data dictionary for rendering the template.
        :rtype: dict
        """
        context = super().get_context_data(**kwargs)
        context["selected"] = "Home"
        projects = Project.get_by_user(self.request.user)

        context.update(self.get_top_vulnerable_projects(projects))

        context["vuln_timeline"] = self.get_timeline(Vulnerability, projects)
        context["finding_timeline"] = self.get_timeline(Finding, projects)
        context["scan_timeline"] = self.get_scan_timeline(projects)

        bundles = Bundle.get_by_owner(self.request.user)
        context["bundle_count"] = len(bundles)
        context["inherited_bundle_count"] = len(
            bundles.filter(~models.Q(owner=self.request.user))
        )

        context["project_count"] = len(projects)
        context["public_project_count"] = len(
            projects.filter(visibility=Visibility.PUBLIC)
        )

        scans = Scan.objects.filter(project__in=projects)
        context["scan_count"] = len(scans)
        context["active_scan_count"] = len(scans.filter(is_active=True))

        teams = Team.get_by_owner(self.request.user)
        context["team_count"] = len(teams)
        context["public_team_count"] = len(teams.filter(visibility=Visibility.PUBLIC))
        return context

    def get_timeline(self, model, projects) -> namespace:
        """
        Retrieve timeline data for a specific model and projects.

        This method retrieves timeline data for a specific model (e.g.,
        :class:`Vulnerability`, :class:`Finding`) associated with the given
        projects. The data includes information about the discovery dates
        and the total count of instances for each date. The data is returned
        as a :class:`namespace` object.

        :param model: The model class for which to retrieve the timeline data.
        :type model: models.Model
        :param projects: The projects to filter the timeline data.
        :type projects: QuerySet
        :return: The timeline data as a :class:`namespace` object.
        :rtype: :class:`namespace`
        """
        data = namespace()
        queryset = model.objects.filter(scan__project__in=projects)
        # Retrieve the objects and count for the timeline
        data.objects = queryset.values("discovery_date").annotate(
            total=models.Count("discovery_date")
        )
        data.count = len(queryset)
        return data


class ProjectsView(VulnContextMixin, ContextMixinBase, TemplateAPIView):
    """
    View class for the projects page.

    This class represents the view for the projects page, which displays information
    about the user's projects and allows project creation. It inherits from several
    mixins to incorporate different functionalities into the view.

    :ivar template_name: The name of the HTML template used for rendering the projects
                         page.
    :vartype template_name: str
    """
    template_name = "dashboard/projects.html"

    def post(self, request, *args, **kwargs):
        """
        Handle the HTTP POST request for project creation.

        This method handles the HTTP POST request when creating a new project. It delegates
        the handling to the :class:`ProjectCreationView` and checks the result status
        code. If the status code indicates an error, an appropriate error message is
        displayed. Finally, the user is redirected back to the projects page.

        :param request: The HTTP POST request object.
        :type request: rest_framework.request.Request
        :return: The HTTP redirect response.
        :rtype: rest_framework.response.Response
        """
        view = rest_project.ProjectCreationView.as_view()
        result = view(request)

        if result.status_code > 400:
            messages.error(request, "Could not create project!")

        return redirect("Projects")

    def get_context_data(self, **kwargs):
        """
        Retrieve the context data for rendering the projects page.

        This method retrieves and prepares the necessary data to be used in the
        template rendering process for the projects page. It includes information
        about project statistics, project table columns, vulnerability statistics,
        and project-specific data for the project table.

        :param kwargs: Additional keyword arguments.
        :return: The context data dictionary for rendering the template.
        :rtype: dict
        """
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
        """
        Retrieve project-specific context data.

        This method retrieves project-specific context data for a given project. It includes information about the
        project itself, vulnerability statistics related to the project, and scan data if available.

        :param project: The project object.
        :type project: Project
        :return: The project-specific context data as a namespace object.
        :rtype: namespace
        """
        data = namespace(project=project)
        data.update(AbstractBaseFinding.stats(Vulnerability, project=project))

        scan = Scan.objects.filter(project=project).order_by("start_date")
        data["scan"] = ScanSerializer(scan[0]).data if len(scan) > 0 else None
        return data


class BundlesView(VulnContextMixin, ContextMixinBase, TemplateAPIView):
    """View class for the bundles page.

    This class represents the view for the bundles page, which displays information
    about the user's bundles. It inherits from several mixins to incorporate different
    functionalities into the view.

    :ivar template_name: The name of the HTML template used for rendering the bundles page.
    :vartype template_name: str
    """
    template_name = "dashboard/bundles.html"

    def get_context_data(self, **kwargs: dict) -> dict:
        """
        Retrieve the context data for rendering the bundles page.

        This method retrieves and prepares the necessary data to be used in the template
        rendering process for the bundles page. It includes information about bundle
        statistics, level data, vulnerability statistics, and bundle-specific data for
        the bundle table.

        :return: The context data dictionary for rendering the template.
        :rtype: dict
        """
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
        """Retrieve level data for the bundles.

        This method retrieves the level data for the bundles, including the count of
        bundles per risk level.

        :return: The level data dictionary.
        :rtype: dict
        """
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
        """Retrieve bundle-specific context data.

        :param bundle: The bundle object.
        :type bundle: Bundle
        :return: The bundle-specific context data as a namespace object.
        :rtype: namespace
        """
        data = namespace(bundle=bundle)
        data.update(AbstractBaseFinding.stats(Vulnerability, bundle=bundle))
        return data


class LicenseView(ContextMixinBase, TemplateAPIView):
    template_name = "license.html"


class PluginsView(ContextMixinBase, TemplateAPIView):
    """
    View class for the plugins page.

    This class represents the view for the plugins page, which displays information
    about plugins and provides functionality related to plugin management.

    :ivar template_name: The name of the HTML template used for rendering the
                         plugins page.
    :vartype template_name: str
    :ivar permission_classes: The permission classes applied to the view.
    :vartype permission_classes: list
    """
    template_name = "plugins/plugins-base.html"
    permission_classes = [
        # External users should not be able to query data from internal
        # configured templates
        ~IsExternal
    ]

    def get_context_data(self, **kwargs: dict) -> dict:
        """Retrieve the context data for rendering the plugins page.

        This method retrieves and prepares the necessary data to be used in the
        template rendering process for the plugins page. It determines the active
        subpage, sets the appropriate context variables, and updates the template
        name accordingly.

        :param kwargs: Additional keyword arguments.
        :return: The context data dictionary for rendering the template.
        :rtype: dict
        """
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
        """Retrieve and provide context data for the scan view.

        This method overrides the base class method to add additional
        context data for rendering the scan view.

        :return: A dictionary containing the context data for the view.
        :rtype: dict
        """
        context = super().get_context_data(**kwargs)
        projects = Project.get_by_user(self.request.user)

        context["scan_table_data"] = self.get_scan_timeline(projects)
        context["scanners"] = ScannerPlugin.all()
        context["available"] = projects
        context["selected"] = "tabs-scans"
        return context

    def post(self, request, *args, **kwargs):
        """Handle the HTTP POST request for creating scans.

        This method is triggered when a user submits a scan creation form.
        """
        view = rest_scan.MultipleScanCreationView.as_view()
        view(request)
        return redirect("Scans", **self.kwargs)
