from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect

from mastf.MASTF.mixins import TemplateAPIView, ContextMixinBase
from mastf.MASTF.permissions import CanViewTeam
from mastf.MASTF.models import Account, Team
from mastf.MASTF.rest.views import TeamCreationView

__all__ = [
    'UserProfileView', 'UserTeamsView', 'UserTeamView'
]

class UserProfileView(ContextMixinBase, TemplateAPIView):
    template_name = "user/settings/settings-account.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["account"] = Account.objects.get(user=self.request.user)
        context["active"] = "account"
        return context

class UserTeamsView(ContextMixinBase, TemplateAPIView):
    template_name = "user/settings/settings-teams.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["teams"] = self.request.user.teams.all()
        context["active"] = "teams"
        context["account"] = Account.objects.get(user=self.request.user)
        context["available"] = list(User.objects.all())
        context["available"].remove(self.request.user)

        return context

    def post(self, request, *args, **kwargs):
        view = TeamCreationView.as_view()
        response = view(request)
        if response.status_code != 201:
            messages.error(request, "Could not create Team!", f"Status-Code: {response.status_code}")

        return redirect("Teams")

class UserTeamView(ContextMixinBase, TemplateAPIView):
    template_name = "user/team.html"
    permission_classes = [CanViewTeam]

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        context["team"] = self.get_object(Team, "pk")
        return context