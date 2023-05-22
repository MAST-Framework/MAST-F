from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from rest_framework.views import APIView
from rest_framework import permissions, authentication, status, exceptions
from rest_framework.response import Response
from rest_framework.request import Request

from mastf.MASTF.serializers import UserSerializer, AccountSerializer
from mastf.MASTF.forms import RegistrationForm, ChangePasswordForm, SetupForm
from mastf.MASTF.models import Account, Environment
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
    "WizardSetupView",
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

    def on_delete(self, request: Request, obj) -> None:
        admin_count = len(Account.objects.filter(role=Role.ADMIN))
        if obj == self.request.user and admin_count == 1:
            # Check whether the user wants to delete the last admin account
            acc = Account.objects.get(user=obj)
            if acc.role == Role.ADMIN:
                raise exceptions.ValidationError(
                    (
                        "You are going to remove the last admin account from this framework "
                        "instance. This action is prohibited by default, because you woudn't "
                        "be able to configure your instance properly after you have removed "
                        "the last administrator."
                    )
                )


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
    """A view for handling API requests related to accounts.

    The ``AccountView`` class defines a view for handling API requests related to
    accounts. The ``prepare_patch`` method is responsible for preparing the
    account update by checking if the user is an administrator and if the ``'ADMIN'``
    role is going to be removed from the last admin account.

    If the user is not an admin, the role field is removed from the update as only
    admins can change user's role's. The method raises a ``ValidationError`` if the
    last admin account tries to remove its admin status.
    """

    serializer_class = AccountSerializer
    model = Account
    permission_classes = [
        # Only authenticated users with permission to view or edit accounts
        # are allowed to make requests.
        permissions.IsAuthenticated & (CanViewAccount | CanEditAccount)
    ]
    bound_permissions = [CanViewAccount]

    def prepare_patch(self, data: dict, instance):
        # The role should be updated by admins only
        if "role" in data:
            if not IsAdmin().has_permission(self.request, self):
                data.pop("role")
            else:
                # We now know that the user is an admin
                admin_count = len(Account.objects.filter(role=Role.ADMIN))
                if admin_count == 1 and instance.user == self.request.user:
                    if data.get("role", "") != Role.ADMIN and instance.role == Role.ADMIN:
                        raise exceptions.ValidationError(
                            (
                                "You can't remove the 'ADMIN' role from the last admin account"
                                "of this framework. You won't be able to edit configuration "
                                "settings any more."
                            )
                        )


class WizardSetupView(APIView):
    """
    A view that handles setting up an initial user account for the wizard.

    This view is designed to be used only once, during the initial setup of
    the wizard.

    The post method of this view handles a ``POST`` request and creates an
    initial user account for the wizard. It first checks if it has already
    been initialized by checking the ``first_start`` attribute of the global
    ``Environment`` object. If the wizard has already been initialized, it
    returns an error response.

    Otherwise, it creates a new ``SetupForm`` object from the request data,
    validates it, and extracts the cleaned data from it. It then creates a
    new user with the provided username and password, and a new account
    object with the new user and a role of ADMIN.

    It assigns various permissions to the new user and the new account, and
    marks the wizard as initialized by setting the ``first_start`` attribute
    of the global ``Environment`` object to ``False``.

    Finally, it displays a message to the user indicating successful setup
    and returns a success response with the new user's primary key.
    """

    def post(self, request, *args, **kwargs):
        """
        Handles a POST request to create an initial user account (ADMIN) for
        the wizard.

        :param request: The HTTP request object.
        :type request: rest_framework.request.Request

        :return: A HTTP response object indicating the result of the request.
        :rtype: rest_framework.response.Response
        """

        env = Environment.env()
        # If the wizard has already been initialized, we shall return an
        # error response
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
        # IMPORTANT: Create a new account object with the new user with a
        # role of ADMIN. Don't forget that as we run into errors if no
        # account is mapped to an existing user.
        acc = Account.objects.create(user=user, role=Role.ADMIN)
        for p in (CanCreateUser, CanDeleteUser, CanEditUser):
            p.assign_to(user, user.pk)

        for p in (CanEditAccount, CanViewAccount):
            p.assign_to(user, acc.pk)

        # Mark the wizard as initialized and save the environment object
        env.first_start = False
        env.save()
        messages.info(self.request, "Finished setup, please log-in to your account!")
        return Response({"success": True, "pk": user.pk})
