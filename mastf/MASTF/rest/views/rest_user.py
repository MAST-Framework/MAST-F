from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from rest_framework.views import APIView
from rest_framework import permissions, authentication, status
from rest_framework.response import Response
from rest_framework.request import Request

from mastf.MASTF.rest.permissions import IsUser, ReadOnly
from mastf.MASTF.serializers import UserSerializer
from mastf.MASTF.forms import RegistrationForm

from .base import APIViewBase

__all__ = [
    'UserView', 'LoginView', 'RegistrationView', 'LogoutView'
]

class UserView(APIViewBase):
    """Sample view for editing and modifying users"""

    # Only an admin or the user itself can push changes to
    # the user account.
    permission_classes = [
        permissions.IsAuthenticated & (IsUser | ReadOnly | permissions.IsAdminUser)
    ]

    model = User
    lookup_field = 'pk'
    serializer_class = UserSerializer

class LoginView(APIView):
    """View class that represents the login endpoint"""

    # We don't have to define any permissions as the login
    # will be the only requestable url.
    authentication_classes = [
        authentication.BasicAuthentication,
        authentication.SessionAuthentication
    ]

    def post(self, request: Request):
        """Authenticates with the given username and password.

        :param request: the HttpRequest
        :type request: Request
        :return: ``400`` on bad credentials, ``401`` on invalid credentials
                 and ``200`` on success
        :rtype: Response
        """
        username = request.data.get('username', None)
        password = request.data.get('password', None)

        if not username or not password:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=username, password=password)
        if not user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        login(request, user)
        return Response({'success': True}, status.HTTP_200_OK)


class RegistrationView(APIView):
    """Endpoint for creating new users.

    By default, new users can be created by administrators only.
    """

    # authentication_classes = [
    #     authentication.BasicAuthentication,
    #     authentication.SessionAuthentication
    # ]

    # permission_classes = [
    #     permissions.IsAdminUser & permissions.IsAuthenticated
    # ]

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

        username = form.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            return Response(data={'message': 'User already present'},
                            status=status.HTTP_409_CONFLICT)

        User.objects.create_user(username=username, password=form.cleaned_data['password'])
        return Response({'success': True}, status.HTTP_200_OK)


class LogoutView(APIView):
    """API endpoint to delegate manual logouts."""

    # Permissions are not required in this API endpoint
    authentication_classes = [
        authentication.BasicAuthentication,
        authentication.SessionAuthentication
    ]

    def post(self, request: Request) -> Response:
        """Performs a logout on the current user.

        :param request: the HttpRequest
        :type request: Request
        :return: a success message
        :rtype: Response
        """
        logout(request)
        return Response({'success': True}, status=status.HTTP_200_OK)
