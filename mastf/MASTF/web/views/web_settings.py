from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect

from rest_framework.permissions import IsAdminUser, exceptions

from mastf.MASTF.mixins import TemplateAPIView, ContextMixinBase
from mastf.MASTF.permissions import CanViewTeam, CanEditUser
from mastf.MASTF.models import Account, Team, Environment, namespace
from mastf.MASTF.utils.enum import Role
from mastf.MASTF.rest.views import TeamCreationView, RegistrationView
from mastf.MASTF.rest.permissions import IsAdmin

__all__ = [
    "UserProfileView",
    "UserTeamsView",
    "UserTeamView",
    "AdminUserConfig",
    "AdminUsersConfiguration",
    "AdminTeamsConfiguration",
    "AdminEnvironmentConfig",
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
        response = view(request, **self.kwargs)
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
    default_redirect = "Teams"

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        context["team"] = self.get_object(Team, "pk")
        return context


class AdminUserConfig(ContextMixinBase, TemplateAPIView):
    template_name = "user/settings/settings-account.html"
    permission_classes = [CanEditUser]
    default_redirect = "Settings"

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
    permission_classes = [IsAdminUser | IsAdmin]
    default_redirect = "Settings"

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)

        context["users"] = Account.objects.all()
        context["active"] = "admin-user-config"
        context["user_roles"] = list(Role)
        return context

    def post(self, *args, **kwargs):
        # Note that we can use this API view here as the user must be an
        # Admin-User.
        view = RegistrationView.as_view()
        response = view(self.request, **self.kwargs)

        if response.status_code != 200:
            messages.warning(
                self.request,
                f"Could not create user: {response.data.get('detail', '')}",
                "ValidationError",
            )
        return redirect("Admin-Users-Config")


class AdminTeamsConfiguration(ContextMixinBase, TemplateAPIView):
    template_name = "user/settings/settings-teams.html"
    default_redirect = "Teams"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["teams"] = Team.objects.all()
        context["active"] = "admin-team-config"
        context["account"] = Account.objects.get(user=self.request.user)
        context["available"] = list(User.objects.all())
        context["available"].remove(self.request.user)
        context["is_admin"] = True
        return context


class AdminEnvironmentConfig(ContextMixinBase, TemplateAPIView):
    template_name = "user/admin/env.html"
    permission_classes = [IsAdminUser | IsAdmin]
    default_redirect = "Settings"

    user_elements = [
        (
            "Allow Teams",
            "allow_teams",
            "Controls whether Teams can be created by users.",
        ),
        (
            "Max Projects",
            "max_projects",
            "Controls the maximum amount of projects per user.",
        ),
        ("Max Teams", "max_teams", "Controls the maximum amount of teams per user."),
        (
            "Max Bundles",
            "max_bundles",
            "Controls the maximum amount of bundles per user.",
        ),
    ]

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        if not self.check_permissions(self.request):
            raise exceptions.ValidationError("Insufficient Permissions")

        context["active"] = "env"

        env = Environment.env()
        user_cat = namespace(name="User-Configuration")
        user_cat.elements = []
        for label, name, hint in self.user_elements:
            user_cat.elements.append(self.get_element(env, label, name, hint))

        auth_cat = namespace(name="Authentication")
        auth_cat.elements = [
            self.get_element(
                env,
                "Allow Registration",
                "allow_registration",
                "Controls whether new users can be created by registration.",
            )
        ]

        context["environment"] = [user_cat, auth_cat]
        return context

    def get_element(
        self, env: Environment, label, name: str, hint: str, disabled=False
    ):
        return namespace(
            name=name,
            value=getattr(env, name),
            hint=hint,
            disabled=disabled,
            label=label,
        )
