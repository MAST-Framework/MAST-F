from django.http import HttpRequest
from django.contrib.auth.mixins import LoginRequiredMixin

from mastf.MASTF import settings
from mastf.MASTF.models import Account

LOGIN_URL = '/web/login'

class ContextMixinBase(LoginRequiredMixin):
    login_url = LOGIN_URL
    
    def prepare_context_data(self, request: HttpRequest, **kwargs) -> dict:
        context = dict(kwargs)
        context['debug'] = settings.DEBUG

        account = Account.objects.filter(user=request.user).first()
        if account and account.role:
            context['user_role'] = account.role

        return context
