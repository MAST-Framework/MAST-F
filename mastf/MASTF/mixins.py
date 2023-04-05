from datetime import datetime

from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from mastf.MASTF import settings
from mastf.MASTF.scanners.plugin import ScannerPlugin
from mastf.MASTF.models import Account, Project, Scan

LOGIN_URL = '/web/login'

class ContextMixinBase(LoginRequiredMixin, TemplateView):
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

    def apply_vuln_context(self, context: dict, vuln: dict) -> None:
        context['vuln_count'] = vuln.get("count", 0)
        context['vuln_data'] = [
            self.get_vuln_context(vuln, "Critical", "pink"),
            self.get_vuln_context(vuln, "High", "red"),
            self.get_vuln_context(vuln, "Medium", "orange"),
            self.get_vuln_context(vuln, "Low", "yellow"),
            self.get_vuln_context(vuln, "Other", "secondary")
        ]

    def get_vuln_context(self, stats: dict, name: str, bg: str) -> dict:
        field = f"{name.lower()}_vuln"
        return {
            'name': name,
            'color': f"bg-{bg}",
            'percent': (stats.get(field, 0) / stats.get('rel_count', 1)) * 100,
            'count': stats.get(field, 0)
        }

class UserProjectMixin:
    
    def apply_project_context(self, context: dict, project_uuid) -> None:
        context['project'] = get_object_or_404(Project.objects.all(), project_uuid=project_uuid)
        context['scanners'] = ScannerPlugin.all()
        
