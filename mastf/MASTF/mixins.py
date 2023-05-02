from datetime import datetime
from typing import Any
from django import http

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework.permissions import BasePermission, exceptions

from mastf.MASTF import settings
from mastf.MASTF.scanners.plugin import ScannerPlugin
from mastf.MASTF.models import Account, Project, Scan

LOGIN_URL = '/web/login'

class TemplateAPIView(TemplateView):
    permission_classes = None

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        # TODO: catch validation errors
        return super().dispatch(request, *args, **kwargs)

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
        assert model is not None, (
            "The stored model must not be null"
        )

        assert pk_field is not None, (
            "The field used for lookup must not be null"
        )

        assert pk_field in self.kwargs, (
            "Invalid lookup field - not included in args"
        )

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
        context['debug'] = settings.DEBUG
        context['today'] = datetime.now()

        account = Account.objects.filter(user=request.user).first()
        if account and account.role:
            context['user_role'] = account.role

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
        context['vuln_count'] = vuln.get("count", 0)
        context['vuln_data'] = [
            self.get_vuln_context(vuln, "Critical", "pink"),
            self.get_vuln_context(vuln, "High", "red"),
            self.get_vuln_context(vuln, "Medium", "orange"),
            self.get_vuln_context(vuln, "Low", "yellow"),
            self.get_vuln_context(vuln, "None", "secondary-lt")
        ]

    def get_vuln_context(self, stats: dict, name: str, bg: str) -> dict:
        field = name.lower()
        return {
            'name': name,
            'color': f"bg-{bg}",
            'percent': (stats.get(field, 0) / stats.get('rel_count', 1)) * 100,
            'count': stats.get(field, 0)
        }



class UserProjectMixin:
    def apply_project_context(self, context: dict) -> None:
        context['project'] = self.get_object(Project, 'project_uuid')
        context['scanners'] = ScannerPlugin.all()

