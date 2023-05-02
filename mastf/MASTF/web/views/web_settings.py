from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect

from rest_framework.permissions import IsAdminUser

from mastf.MASTF.mixins import TemplateAPIView, ContextMixinBase
from mastf.MASTF.permissions import CanViewTeam, CanEditUser
from mastf.MASTF.models import Account, Team
from mastf.MASTF.utils.enum import Role
from mastf.MASTF.rest.views import TeamCreationView, RegistrationView

__all__ = [
    "UserProfileView",
    "UserTeamsView",
    "UserTeamView",
    "AdminUserConfig",
    "AdminUsersConfiguration",
    "AdminTeamsConfiguration"
]


class UserProfileView(ContextMixinBase, TemplateAPIView):
    template_name = "user/settings/settings-account.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["account"] = Account.objects.get(user=self.request.user)
        context["active"] = "account"
        context["user"] = self.request.user
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
            messages.error(
                request,
                "Could not create Team!",
                f"Status-Code: {response.status_code}",
            )

        return redirect("Teams")


class UserTeamView(ContextMixinBase, TemplateAPIView):
    template_name = "user/team.html"
    permission_classes = [CanViewTeam]

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        context["team"] = self.get_object(Team, "pk")
        return context


class AdminUserConfig(ContextMixinBase, TemplateAPIView):
    template_name = "user/settings/settings-account.html"
    permission_classes = [CanEditUser]

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        user = self.get_object(User, "pk")
        context["user"] = user
        context["account"] = Account.objects.get(user=user)
        context["active"] = "admin-user-config"
        context["is_admin"] = True
        context["user_roles"] = list(Role)
        return context


class AdminUsersConfiguration(ContextMixinBase, TemplateAPIView):
    template_name = "user/admin/users.html"
    permission_classes = [IsAdminUser]

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        self.check_permissions(self.request)

        context["users"] = Account.objects.all()
        context["active"] = "admin-user-config"
        return context

    def post(self, *args, **kwargs):
        # TODO: outsource this method call to dispatch()
        self.check_permissions(self.request)
        # Note that we can use this API view here as the user must be an
        # Admin-User.
        view = RegistrationView()
        response = view(**self.kwargs)

        if response.status_code != 200:
            messages.warning(self.request, f"Could not create user: {response.data.get('detail', '')}",
                             "ValidationError")
        return redirect


class AdminTeamsConfiguration(ContextMixinBase, TemplateAPIView):
    template_name = "user/settings/settings-teams.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["teams"] = Team.objects.all()
        context["active"] = "admin-team-config"
        context["account"] = Account.objects.get(user=self.request.user)
        context["available"] = list(User.objects.all())
        context["available"].remove(self.request.user)
        context["is_admin"] = True
        return context
