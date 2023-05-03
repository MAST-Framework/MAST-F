from django.db.models import Count, Case, When

from mastf.MASTF.mixins import ContextMixinBase, VulnContextMixin, TemplateAPIView
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


class BundleDetailsView(ContextMixinBase, VulnContextMixin, TemplateAPIView):
    template_name = "bundle/bundle-overview.html"
    permission_classes = [CanViewBundle]
    default_redirect = "Bundles"

    def get_context_data(self, **kwargs: dict) -> dict:
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

        return context

    def _apply_bundle_projects(self, bundle: Bundle) -> dict:
        data = namespace()
        projects = bundle.projects.all()

        data.project_table_data = []
        for project in projects:
            pdata = AbstractBaseFinding.stats(Vulnerability, project=project)
            pdata["project"] = project
            data.project_table_data.append(pdata)

        return data

    def _apply_bundle_overview(self, bundle: Bundle) -> dict:
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

        pks = [x.pk for x in bundle.projects.all()]
        cases = {}
        for severity in [str(x) for x in Severity]:
            name = f"{severity.lower()}_vuln"
            cases[name] = Count(Case(When(severity=severity.lower(), then=1)))

        # FIrst, we use the annotate() method to add computed fields to each Project object
        # in the queryset. These fields count the number of vulnerabilities of each severity
        # level for each project, using Case and When expressions. We also add a "total"
        # field that counts the total number of vulnerabilities for each project.
        #
        # Finally, we use the order_by() method to sort the projects by their number of critical,
        # high, medium, low, ... vulnerabilities, as well as their total number of vulnerabilities.
        # We use the - sign before each field name to sort in descending order.
        #
        # This query should return a queryset of Project objects, sorted by their number of
        # vulnerabilities, with higher weights for critical vulnerabilities.
        vuln = (
            Vulnerability.objects.filter(scan__project__pk__in=pks)
            .values("severity", "scan__project", "pk")
            .annotate(**cases)
            .annotate(total=Count("pk"))
            .order_by(*[f"-{x}" for x in cases])
        )
        if len(vuln) >= 1:
            data.top_vuln_first = Project.objects.get(pk=vuln[0]["scan__project"])
        if len(vuln) >= 2:
            data.top_vuln_second = Project.objects.get(pk=vuln[1]["scan__project"])
        if len(vuln) >= 3:
            data.top_vuln_third = Project.objects.get(pk=vuln[2]["scan__project"])

        return data
