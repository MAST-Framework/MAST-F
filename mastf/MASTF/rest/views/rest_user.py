from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from rest_framework.views import APIView
from rest_framework import permissions, authentication, status
from rest_framework.response import Response
from rest_framework.request import Request

from mastf.MASTF.serializers import (
    UserSerializer,
    AccountSerializer
)
from mastf.MASTF.forms import (
    RegistrationForm,
    ChangePasswordForm,
    SetupForm
)
from mastf.MASTF.models import (
    Account,
    Environment
)
from mastf.MASTF.utils.enum import Role
from mastf.MASTF.rest.permissions import IsAdmin
from mastf.MASTF.permissions import (
    CanEditUser,
    CanDeleteUser,
    CanViewAccount,
    CanEditAccount,
    CanCreateUser,
)

from .base import APIViewBase, GetObjectMixin

__all__ = [
    "UserView",
    "LoginView",
    "RegistrationView",
    "LogoutView",
    "AccountView",
    "ChangePasswordView",
    "WizardSetupView"
]


class UserView(APIViewBase):
    """Sample view for editing and modifying users"""

    # Only an admin or the user itself can push changes to
    # the user account.
    permission_classes = [
        permissions.IsAuthenticated
        & (
            # Note that CanDeleteUser will only check if the request's
            # method is DELETE.
            CanDeleteUser
            | CanEditUser
        )
    ]
    bound_permissions = [CanEditUser, CanDeleteUser]
    model = User
    lookup_field = "pk"
    serializer_class = UserSerializer


class LoginView(APIView):
    """View class that represents the login endpoint"""

    # We don't have to define any permissions as the login
    # will be the only requestable url.
    authentication_classes = [
        authentication.BasicAuthentication,
        authentication.SessionAuthentication,
    ]

    def post(self, request: Request):
        """Authenticates with the given username and password.

        :param request: the HttpRequest
        :type request: Request
        :return: ``400`` on bad credentials, ``401`` on invalid credentials
                 and ``200`` on success
        :rtype: Response
        """
        username = request.data.get("username", None)
        password = request.data.get("password", None)

        if not username or not password:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=username, password=password)
        if not user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        login(request, user)
        return Response({"success": True}, status.HTTP_200_OK)


# TODO: manage access for creation of users
class RegistrationView(APIView):
    """Endpoint for creating new users."""

    def post(self, request: Request):
        """Creates a new user in the shared database.

        :param request: the HttpRequest
        :type request: Request
        :return: ``400`` on invalid form data, ``409`` if a user
                 with the given username already exists or ``200``
                 on success.
        :rtype: Response
        """
        form = RegistrationForm(request.data)
        if not form.is_valid():
            return Response(form.errors, status.HTTP_400_BAD_REQUEST)

        is_admin = IsAdmin().has_permission(self.request, self)
        if not Environment.env().allow_registration and not is_admin:
            return Response(
                data={"detail": "Registration not allowed"},
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        username = form.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            return Response(
                data={"detail": "User already present"},
                status=status.HTTP_409_CONFLICT,
            )

        user = User.objects.create_user(
            username=username, password=form.cleaned_data["password"]
        )
        acc = Account.objects.create(user=user)

        role = form.cleaned_data["role"]
        if role and is_admin:
            acc.role = role
            acc.save()

        CanDeleteUser.assign_to(user, user.pk)
        CanEditUser.assign_to(user, user.pk)
        CanViewAccount.assign_to(user, acc.pk)
        CanEditAccount.assign_to(user, acc.pk)
        return Response({"success": True, "pk": user.pk}, status.HTTP_200_OK)


class LogoutView(APIView):
    """API endpoint to delegate manual logouts."""

    # Permissions are not required in this API endpoint
    authentication_classes = [
        authentication.BasicAuthentication,
        authentication.SessionAuthentication,
    ]

    def post(self, request: Request) -> Response:
        """Performs a logout on the current user.

        :param request: the HttpRequest
        :type request: Request
        :return: a success message
        :rtype: Response
        """
        logout(request)
        return Response({"success": True}, status=status.HTTP_200_OK)


class ChangePasswordView(GetObjectMixin, APIView):
    authentication_classes = [
        authentication.BasicAuthentication,
        authentication.SessionAuthentication,
        authentication.TokenAuthentication,
    ]
    model = User
    permission_classes = [permissions.IsAuthenticated & CanEditUser]

    def patch(self, *args, **kwargs):
        user: User = self.get_object()

        form = ChangePasswordForm(self.request.data)
        success = False
        if form.is_valid():
            user.set_password(form.cleaned_data["password"])
            user.save()

            logout(self.request)
            success = True

        return Response({"success": success})


class AccountView(APIViewBase):
    serializer_class = AccountSerializer
    model = Account
    permission_classes = [
        permissions.IsAuthenticated & (CanViewAccount | CanEditAccount)
    ]
    bound_permissions = [CanViewAccount]

    def prepare_patch(self, data: dict):
        # The role should be updated by admins only
        if not bool(self.request.user and self.request.user.is_staff):
            if "role" in data:
                data.pop("role")


class WizardSetupView(APIView):
    def post(self, request, *args, **kwargs):
        env = Environment.env()
        if not env.first_start:
            return Response(
                {"detail": "Already initialized", "success": False},
                status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        form = SetupForm(request.data)
        if not form.is_valid():
            return Response(
                {"success": False, "detail": str(form.errors)},
                status.HTTP_400_BAD_REQUEST,
            )

        data = form.cleaned_data
        user = User.objects.create_user(
            username=data["username"], password=data["password"]
        )
        acc = Account.objects.create(user=user, role=Role.ADMIN)
        for p in (CanCreateUser, CanDeleteUser, CanEditUser):
            p.assign_to(user, user.pk)

        for p in (CanEditAccount, CanViewAccount):
            p.assign_to(user, acc.pk)

        env.first_start = False
        env.save()
        messages.info(self.request, "Finished setup, please log-in to your account!")
        return Response({'success': True, 'pk': user.pk})
