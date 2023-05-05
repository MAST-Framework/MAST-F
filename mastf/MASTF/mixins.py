from datetime import datetime

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView
from django.db import models
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework.permissions import BasePermission, exceptions

from mastf.MASTF import settings
from mastf.MASTF.utils.enum import Severity, Visibility
from mastf.MASTF.scanners.plugin import ScannerPlugin
from mastf.MASTF.models import (
    Account,
    Project,
    namespace,
    Vulnerability,
    Scan,
    AbstractBaseFinding,
    Finding
)


LOGIN_URL = "/web/login"


class TemplateAPIView(TemplateView):
    permission_classes = None
    default_redirect = "Dashboard"

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        try:
            self.check_permissions(request)
            return super().dispatch(request, *args, **kwargs)
        except exceptions.ValidationError as err:
            messages.error(request, str(err.detail), err.__class__.__name__)
            return self.on_dispatch_error()

    def on_dispatch_error(self):
        return redirect(self.default_redirect, *self.args, **self.kwargs)

    def check_object_permissions(self, request, obj) -> bool:
        if self.permission_classes:
            for permission in self.permission_classes:
                # Rather use an additional instance check here instead of
                # throwing an exception
                if isinstance(permission, BasePermission):
                    if not permission.has_object_permission(request, self, obj):
                        return False
        # Return Ture by default
        return True

    def check_permissions(self, request):
        if self.permission_classes:
            for permission in self.permission_classes:
                if not permission().has_permission(request, self):
                    raise exceptions.ValidationError("Insufficient permisions")
        # Return Ture by default
        return True

    def get_object(self, model, pk_field: str):
        """Returns a project mapped to a given primary key

        :return: the instance of the desired model
        :rtype: ? extends Model
        """
        assert model is not None, "The stored model must not be null"

        assert pk_field is not None, "The field used for lookup must not be null"

        assert pk_field in self.kwargs, "Invalid lookup field - not included in args"

        instance = get_object_or_404(
            model.objects.all(), **{pk_field: self.kwargs[pk_field]}
        )
        if not self.check_object_permissions(self.request, instance):
            raise exceptions.ValidationError("Insufficient permissions", 500)

        return instance


class ContextMixinBase(LoginRequiredMixin):
    login_url = LOGIN_URL

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        context.update(self.prepare_context_data(self.request))
        return context

    def prepare_context_data(self, request: HttpRequest, **kwargs) -> dict:
        context = dict(kwargs)
        context["debug"] = settings.DEBUG
        context["today"] = datetime.now()

        account = Account.objects.filter(user=request.user).first()
        if account and account.role:
            context["user_role"] = account.role

        return context


class VulnContextMixin:
    colors = {
        "critical": "pink",
        "high": "red",
        "medium": "orange",
        "low": "yellow",
        "other": "secondary",
        "none": "secondary-lt",
    }

    def apply_vuln_context(self, context: dict, vuln: dict) -> None:
        context["vuln_count"] = vuln.get("count", 0)
        context["vuln_data"] = [
            self.get_vuln_context(vuln, "Critical", "pink"),
            self.get_vuln_context(vuln, "High", "red"),
            self.get_vuln_context(vuln, "Medium", "orange"),
            self.get_vuln_context(vuln, "Low", "yellow"),
            self.get_vuln_context(vuln, "None", "secondary-lt"),
        ]

    def get_vuln_context(self, stats: dict, name: str, bg: str) -> dict:
        field = name.lower()
        return {
            "name": name,
            "color": f"bg-{bg}",
            "percent": (stats.get(field, 0) / stats.get("rel_count", 1)) * 100,
            "count": stats.get(field, 0),
        }


class UserProjectMixin:
    def apply_project_context(self, context: dict) -> None:
        context["project"] = self.get_object(Project, "project_uuid")
        context["scanners"] = ScannerPlugin.all()


class TopVulnerableProjectsMixin:
    def get_top_vulnerable_projects(self, projects: list) -> namespace:
        data = namespace()
        pks = [x.pk for x in projects]
        cases = {}
        for severity in [str(x) for x in Severity]:
            name = f"{severity.lower()}_vuln"
            cases[name] = models.Count(
                models.Case(models.When(severity=severity.lower(), then=1))
            )

        # First, we use the annotate() method to add computed fields to each Project object
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
            .annotate(total=models.Count("pk"))
            .order_by(*[f"-{x}" for x in cases])
        )
        if len(vuln) >= 1:
            data.top_vuln_first = Project.objects.get(pk=vuln[0]["scan__project"])
        if len(vuln) >= 2:
            data.top_vuln_second = Project.objects.get(pk=vuln[1]["scan__project"])
        if len(vuln) >= 3:
            data.top_vuln_third = Project.objects.get(pk=vuln[2]["scan__project"])

        return data


class ScanTimelineMixin:
    def get_scan_timeline(self, projects):
        visibility_level = [str(x).upper() for x in Visibility]
        for name in visibility_level:
            if self.request.GET.get(name.lower(), "true").lower() != "true":
                visibility_level.remove(name)

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

        return scan_table_data