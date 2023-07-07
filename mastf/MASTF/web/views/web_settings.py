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
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect

from rest_framework.permissions import IsAdminUser, exceptions

from mastf.MASTF import settings
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

class SettingsMixin:
    def is_admin(self, user: User) -> bool:
        return Account.objects.get(user=user).role == Role.ADMIN or user.is_staff


class UserProfileView(ContextMixinBase, SettingsMixin, TemplateAPIView):
    """
    A view for displaying the user profile settings.
    """

    template_name = "user/settings/settings-account.html"

    def get_context_data(self, **kwargs):
        """
        Retrieve and prepare the context data for rendering the user profile view.

        :param kwargs: Additional keyword arguments.
        :return: A dictionary containing the context data.
        """
        context = super().get_context_data(**kwargs)
        context["account"] = Account.objects.get(user=self.request.user)
        context["active"] = "account"
        context["is_admin"] = self.is_admin(self.request.user)
        context["user"] = self.request.user
        return context


class UserTeamsView(ContextMixinBase, SettingsMixin, TemplateAPIView):
    """
    A view for displaying the user's teams and team settings.
    """

    template_name = "user/settings/settings-teams.html"

    def get_context_data(self, **kwargs):
        """
        Retrieve and prepare the context data for rendering the user's teams view.

        :param kwargs: Additional keyword arguments.
        :return: A dictionary containing the context data.
        """
        context = super().get_context_data(**kwargs)
        context["teams"] = self.request.user.teams.all()
        context["active"] = "teams"
        context["is_admin"] = self.is_admin(self.request.user)
        context["account"] = Account.objects.get(user=self.request.user)
        context["available"] = list(User.objects.all())
        context["available"].remove(self.request.user)

        return context

    def post(self, request, *args, **kwargs):
        """
        Handle the POST request for creating a new team.

        :param request: The HTTP request object.
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: A redirect response.
        """
        view = TeamCreationView.as_view()
        response = view(request, **self.kwargs)
        if response.status_code != 201:
            messages.error(
                request,
                "Could not create Team!",
                f"Status-Code: {response.status_code}",
            )

        return redirect("Teams")


class UserTeamView(ContextMixinBase, SettingsMixin, TemplateAPIView):
    """
    A view for displaying the details of a specific team.
    """

    template_name = "user/team.html"
    permission_classes = [CanViewTeam]
    default_redirect = "Teams"
    keep_redirect_kwargs = False

    def get_context_data(self, **kwargs: dict) -> dict:
        """
        Retrieve and prepare the context data for rendering the team view.

        :param kwargs: Additional keyword arguments.
        :return: A dictionary containing the context data.
        """
        context = super().get_context_data(**kwargs)
        context["team"] = self.get_object(Team, "pk")
        context["is_admin"] = self.is_admin(self.request.user)
        return context


class AdminUserConfig(ContextMixinBase, SettingsMixin, TemplateAPIView):
    template_name = "user/settings/settings-account.html"
    permission_classes = [CanEditUser]
    default_redirect = "Settings"
    keep_redirect_kwargs = False

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        user = self.get_object(User, "pk")
        context["user"] = user
        context["is_admin"] = self.is_admin(self.request.user)
        context["account"] = Account.objects.get(user=user)
        context["active"] = "admin-user-config"
        context["user_roles"] = list(Role)
        return context


class AdminUsersConfiguration(ContextMixinBase, SettingsMixin, TemplateAPIView):
    template_name = "user/admin/users.html"
    permission_classes = [IsAdminUser | IsAdmin]
    default_redirect = "Settings"
    keep_redirect_kwargs = False

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        context["is_admin"] = self.is_admin(self.request.user)
        context["users"] = Account.objects.all()
        context["active"] = "admin-user-config"
        context["user_roles"] = list(Role)
        context["MASTF_PASSWD_MIN_LEN"] = settings.MASTF_PASSWD_MIN_LEN
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


class AdminTeamsConfiguration(ContextMixinBase, SettingsMixin, TemplateAPIView):
    template_name = "user/settings/settings-teams.html"
    default_redirect = "Teams"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["teams"] = Team.objects.all()
        context["active"] = "admin-team-config"
        context["account"] = Account.objects.get(user=self.request.user)
        context["available"] = list(User.objects.all())
        context["available"].remove(self.request.user)
        context["is_admin"] = self.is_admin(self.request.user)
        return context


class AdminEnvironmentConfig(ContextMixinBase, SettingsMixin, TemplateAPIView):
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
        context["env"] = env
        context["is_admin"] = self.is_admin(self.request.user)
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
