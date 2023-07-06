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
__doc__ = """
This module covers useful mixins for views that are used for displayed
the web-frontend. All views that should only be accessible after a user
login should extend the :class:`ContextMixinBase` class to apply default
context data automatically.
"""
import logging

from datetime import datetime

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView
from django.db import models
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework.permissions import BasePermission, exceptions

from mastf.MASTF import settings
from mastf.MASTF.utils.error import get_error
from mastf.MASTF.utils.enum import Severity, Visibility
from mastf.MASTF.scanners.plugin import ScannerPlugin
from mastf.MASTF.models import (
    Account,
    Project,
    namespace,
    Vulnerability,
    Scan,
    AbstractBaseFinding,
    Finding,
)

logger = logging.getLogger(__name__)


class TemplateAPIView(TemplateView):
    """Base class for all Django views that use templates to render HTML responses.

    This class is a subclass of Django's built-in ``TemplateView`` class, and
    provides additional functionality explicitly for web views. Specifically, the
    :class:`TemplateAPIView` class includes methods for serializing and deserializing
    data to and from HTML templates, which can be used to build custom HTML forms
    or display data in a structured way.

    To use this class, simply subclass it in your Django views and specify the
    template file to use via the *template_name* attribute. You can then use the
    *get_context_data* method to pass additional context variables to the template, and
    the *render_to_response* method to render the response using the specified template.

    In addition, this view implements permission checks that will be applied before any
    incoming request will be handled. Simply specify permission classes or use
    :class:`BoundPermission` objects in a list within the *permission_classes* attribute.

    For example:

    .. code-block:: python
        :linenos:

        from rest_framework.permissions import IsAdmin

        class MyWebView(TemplateAPIView):
            template_name =  'my_template.html'
            permission_classes = [ IsAdmin ]

    This class also includes a *default_redirect* attribute, which can be set to a view
    name that the view will redirect to if an error occurs during processing. If
    'default_redirect' is not set, the view will redirect to the dashboard page.
    """

    permission_classes = None
    """Object or request-level permission classes.

    :type: ``list`` | ``tuple`` | ``Iterable[type | BoundPermission]``
    """

    default_redirect = "Dashboard"
    """Redirect view name to render if an error occurs."""

    keep_redirect_kwargs = True
    """Tell the API view to keep args on redirect."""

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        try:
            self.check_permissions(request)
            return super().dispatch(request, *args, **kwargs)
        except exceptions.ValidationError as err:
            messages.error(request, get_error(err), err.__class__.__name__)
            return self.on_dispatch_error()

    def on_dispatch_error(self):
        """Redirects to a default page if an exception was raised"""
        page = self.default_redirect or "Dashboard"
        kwargs = self.kwargs
        if not self.keep_redirect_kwargs:
            kwargs = self.get_redirect_kwargs()

        return redirect(page, **kwargs)

    def check_object_permissions(self, request, obj) -> bool:
        """Validates if the current user has appropriate permissions to access the given object."""
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
        """Validates whether the request's user has permissions to access this view."""
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

    def get_redirect_kwargs(self) -> dict:
        return {}


class ContextMixinBase(LoginRequiredMixin):
    """A Django mixin that provides additional context variables to a view.

    This mixin adds the following context variables to the view:

    - ``debug``: a boolean value indicating whether the application has been started
                 in debug mode.
    - ``today``: a datetime object representing today's date.
    - ``user_role``: a string representing the user's role.

    To use this mixin, simply include it in your Django view by subclassing it in your
    view class and adding it to the list of mixins in the class definition. For example:

    .. code-block:: python
        :linenos:

        from mastf.MASTF.mixins import ContextMixinBase, TemplateAPIView

        class MyView(ContextMixinBase, TemplateAPIView):
            template_name = "my_template.html"

    You can then access the added context variables in your template as usual,
    for instance:

    .. code-block:: html+django
        :linenos:

        {% if debug %}
        <p>Debug mode is enabled.</p>
        {% endif %}
        <p>Today's date is {{ today|date:"F j, Y" }}.</p>

        {% if user_role == "admin" %}
        <p>You have administrative privileges.</p>
        {% else %}
        <p>You do not have administrative privileges.</p>
        {% endif %}

    For more information on how to use context variables this class provides, see the
    Django's documentation on templates and context processors.
    """

    login_url = "/web/login"
    """Default login URL."""

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        context.update(self.prepare_context_data(self.request))
        return context

    def prepare_context_data(self, request: HttpRequest, **kwargs) -> dict:
        """Inserts additional fields into the context of this view."""
        context = dict(kwargs)
        context["debug"] = settings.DEBUG
        context["today"] = datetime.now()

        try:
            account = Account.objects.get(user=request.user)
            if account and account.role:
                context["user_role"] = account.role
        except Account.MultipleObjectsReturned:
            logger.warning("Multiple Account instances for user: %s", request.user)
        except Account.DoesNotExist:
            logger.error("Could not find Account linked to: %s", request.user)

        return context


class VulnContextMixin:
    """Mixin that applies vulnerability statistics to the context of a view."""

    colors = {
        "critical": "pink",
        "high": "red",
        "medium": "orange",
        "low": "yellow",
        "none": "secondary-lt",
    }

    def apply_vuln_context(self, context: dict, vuln: dict) -> None:
        """Inserts vulnerability data according to the given input stats.

        :param context: the view's context
        :type context: dict
        :param vuln: the vulnerability stats aquired via ``AbstractBaseFinding.stats(...)``
        :type vuln: dict
        """
        context["vuln_count"] = vuln.get("count", 0)
        context["vuln_data"] = [
            self.get_vuln_context(vuln, Severity.CRITICAL.value, "pink"),
            self.get_vuln_context(vuln, Severity.HIGH.value, "red"),
            self.get_vuln_context(vuln, Severity.MEDIUM.value, "orange"),
            self.get_vuln_context(vuln, Severity.LOW.value, "yellow"),
            self.get_vuln_context(vuln, Severity.NONE.value, "secondary-lt"),
        ]

    def get_vuln_context(self, stats: dict, name: str, bg: str) -> dict:
        """Returns HTML information about a vulnerability statistic.

        The returned object has the following structure:

        .. code:: json

            {
                "name": "...",
                "color": "bg-${color}",
                "percent": "...",
                "count": "..."
            }

        :param stats: single vulnerablity statistics according to severity
        :type stats: dict
        :param name: severity name
        :type name: str
        :param bg: the background color
        :type bg: str
        :return: a dictionary storing data for HTML templates
        :rtype: dict
        """
        field = name.lower()
        return {
            "name": name,
            "color": f"bg-{bg}",
            "percent": (stats.get(field, 0) / stats.get("rel_count", 1)) * 100,
            "count": stats.get(field, 0),
        }


class UserProjectMixin:
    """Mixin that adds project-related context variables to a view.

    This mixin provides the *apply_project_context* method, which adds the following
    context variables to the view:

    - ``project``: the Project object corresponding to the *project_uuid* URL parameter.
    - ``scanners``: a list of available scanner plugins.

    To use this mixin, include it in your Django view by subclassing it in your view
    class and adding it to the list of mixins in the class definition. For example:

    .. code-block:: python
        :linenos:

        from django.views.generic import DetailView
        from mastf.MASTF.mixins import UserProjectMixin, TemplateAPIView
        from mastf.MASTF.models import Project

        class MyDetailView(UserProjectMixin, TemplateAPIView):
            model = Project
            template_name = "project_detail.html"

            def get_context_data(self, **kwargs):
                context = super().get_context_data(**kwargs)
                self.apply_project_context(context)
                # add additional context variables here if needed
                return context

    You can then access the added context variables in your template as usual:

    .. code-block:: html+django
        :linenos:

        <h1>Project: {{ project.name }}</h1>
        <p>Available scanners:</p>
        <ul>
            {% for scanner in scanners %}
                <li>{{ scanner.name }}</li>
            {% endfor %}
        </ul>
    """

    def apply_project_context(self, context: dict) -> None:
        context["project"] = self.get_object(Project, "project_uuid")
        context["scanners"] = ScannerPlugin.all()


class TopVulnerableProjectsMixin:
    """Mixin that filters for the most vulnerable project.

    Returns a namespace object (dictionary) that includes the following attribures:

    - ``top_vuln_first`` (**optional**): the most vulnerable project (object)
    - ``top_vuln_second`` (**optional**): the second most vulnerable project (object)
    - ``top_vuln_third`` (**optional**): the third most vulnerable project (object)
    """

    def get_top_vulnerable_projects(self, projects: list) -> namespace:
        """Returns up to three top vulnerable projects of the given list.

        :param projects: the projects (actual project objects)
        :type projects: list
        :return: a dictionary covering the most vulnerable projects.
        :rtype: :class:`namespace`
        """
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
    """Simple mixin class that provides a function to collect scan data.

    The returned data may be used as timeline data or display values in a
    table. Note that the number of included scans can be reduced with the
    following *GET* parameters:

    - ``public``: should be ``true`` to include public projects
    - ``private``: should be ``true`` to include private projects
    - ``internal``: should be ``true`` to include projects a user has access to
    """

    def get_scan_timeline(self, projects):
        """Collects information about scans from the given projects.

        :param projects: the initial project list
        :type projects: list[:class:`Project`]
        :return: a list storing all scans with additional vulnerability stats
        :rtype: list[:class:`namespace`]
        """
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
