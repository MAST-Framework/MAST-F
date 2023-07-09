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
from django.db.models import Count

from mastf.MASTF.mixins import (
    ContextMixinBase,
    VulnContextMixin,
    TemplateAPIView,
    TopVulnerableProjectsMixin,
    )
from mastf.MASTF.models import (
    Bundle,
    Project,
    namespace,
    AbstractBaseFinding,
    Vulnerability,
)
from mastf.MASTF.utils.enum import Severity

from mastf.MASTF.permissions import CanViewBundle

__all__ = ["BundleDetailsView"]


class BundleDetailsView(ContextMixinBase, VulnContextMixin,
                        TopVulnerableProjectsMixin, TemplateAPIView):
    """A view for displaying details of a bundle, including projects and vulnerabilities."""

    template_name = "bundle/bundle-overview.html"
    permission_classes = [CanViewBundle]
    default_redirect = "Bundles"
    keep_redirect_kwargs = False

    def get_context_data(self, **kwargs: dict) -> dict:
        """
        Retrieve and prepare the context data for rendering the bundle details view.

        :param kwargs: Additional keyword arguments.
        :return: A dictionary containing the context data.
        """
        context = super().get_context_data(**kwargs)
        context["bundle"] = self.get_object(Bundle, pk_field="bundle_id")

        available = []
        projects = context["bundle"].projects.all()
        for project in Project.get_by_user(self.request.user):
            if project not in projects:
                available.append(project)

        context["available"] = available
        context["vuln_types"] = [str(x) for x in Severity]

        if self.request.path.endswith("/projects"):
            context["active"] = "tabs-projects"
            context.update(self._apply_bundle_projects(context["bundle"]))
        else:
            context["active"] = "tabs-overview"
            context.update(self._apply_bundle_overview(context["bundle"]))
            context.update(self.get_top_vulnerable_projects(context["bundle"].projects.all()))

        return context

    def _apply_bundle_projects(self, bundle: Bundle) -> dict:
        """
        Apply bundle information to the context for displaying projects.

        :param bundle: The bundle object.
        :return: A dictionary containing the context data for projects.
        """
        data = namespace()
        projects = bundle.projects.all()

        data.project_table_data = []
        for project in projects:
            pdata = AbstractBaseFinding.stats(Vulnerability, project=project)
            pdata["project"] = project
            data.project_table_data.append(pdata)

        return data

    def _apply_bundle_overview(self, bundle: Bundle) -> dict:
        """
        Apply bundle information to the context for displaying an overview.

        :param bundle: The bundle object.
        :return: A dictionary containing the context data for the overview.
        """
        data = namespace()
        data.risk_level = []
        data.vuln_data = []

        self.apply_vuln_context(
            data, AbstractBaseFinding.stats(Vulnerability, bundle=bundle)
        )
        filtered = (
            bundle.projects.values("risk_level")
            .annotate(count=Count("risk_level"))
            .order_by("risk_level")
        )

        amount = len(bundle.projects.all()) or 1
        for category in filtered:
            level = {"name": str(category["risk_level"]), "count": category["count"]}
            level["color"] = self.colors.get(level["name"].lower(), "none")
            level["percent"] = (level["count"] // amount) * 100
            data.risk_level.append(level)

        return data
