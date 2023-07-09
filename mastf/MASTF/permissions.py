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
__doc__ = """
Enriched permissions that can be combined with REST framework's permission
classes. Use classes defined here to restrict access to different resources
and create, assign and delete permissions at runtime.

.. important::
    Administrators will always be able to perform actions on resources as they
    automatically inherit all permissions.

"""

import logging

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission, User
from django.db import connection

from rest_framework.permissions import (
    BasePermission,
    SAFE_METHODS,
    OperationHolderMixin,
)
from rest_framework.exceptions import ValidationError

from mastf.MASTF.utils.enum import Role
from mastf.MASTF.models import Team, Project, Bundle, Account


logger = logging.getLogger(__name__)


class _Method(OperationHolderMixin, BasePermission):
    """
    A mixin that restricts access to a view based on the request method.

    :ivar methods: A list of allowed request methods.
    :vartype methods: list

    This class should not be used directly. Instead, use one of the following
    class attributes to create a new instance:

    * `Delete`: Only allows ``DELETE`` requests.
    * `Post`: Only allows ``POST`` requests.
    * `Patch`: Only allows ``PATCH`` requests.
    * `Get`: Only allows ``GET`` requests.
    * `Put`: Only allows ``PUT`` requests.

    When a new instance is created, the allowed request methods are passed as
    arguments. If no arguments are provided, SAFE_METHODS (which includes GET,
    HEAD, and OPTIONS) will be used by default.

    The _Method class is made callable so that it can be used by the Django REST
    framework even though an instance has been created already.
    """

    def __init__(self, *args) -> None:
        """
        Initialize the `_Method` object.

        :param args: A list of allowed request methods.
        :type args: tuple | Iterable[str]
        """
        self.methods = list(args) or SAFE_METHODS

    def __call__(self, *args, **kwargs):
        # same as defined in BoundPermission, we have to define
        # this object to be callable to prevent errors.
        return self

    def __repr__(self) -> str:
        """
        Return a string representation of the ``_Method`` object.

        :return: A string representation of the allowed methods.
        :rtype: str
        """
        return str(self.methods)

    def has_permission(self, request, view):
        """
        Check if the request method is allowed.

        :param request: The incoming request.
        :type request: rest_framework.request.Request
        :param view: The view being accessed.
        :type view: rest_framework.views.APIView
        :return: ``True`` if the request method is allowed, ``False`` otherwise.
        :rtype: bool
        """
        return request.method in self.methods


# Below, standard methods are instantiated to allow basic permission creation.
Delete = _Method("DELETE")
Post = _Method("POST")
Patch = _Method("PATCH")
Get = _Method("GET")
Put = _Method("PUT")


class BoundPermission(OperationHolderMixin, BasePermission):
    """Class that implements an advanced permission structure for the Django Rest Framework.

    ``BoundPermission`` objects are used within :class:`ManyToManySerializer` classes and
    APIView classes defined in the ``rest.views.base`` module of this project. They integrate
    this utility class so that permissions will be automatically added or removed from a user.

    For instance, the following code creates a simple ``APIView`` that assigns a permission
    named ``CanEditArticle`` to a user:

    .. code-block:: python

        CanEditArticle = BoundPermission(
            "can_edit_article_%s", "Can modify atricles", Article,
            runtime=True, methods=[Patch]
        )

        class ArticleAPIView(APIViewBase):
            ... # authentication related classes
            model = Article
            serializer_class = ArticleSerializer
            bound_permissions = [CanEditArticle]

    The defined permission will be removed automatically if a ``DELETE`` request is made and
    the database object is going to be removed.

    :param codename: A string representing the codename of the permission.
    :type codename: str
    :param name: A string representing the name of the permission.
    :type name: str
    :param model: A Python class representing the model that this permission is associated with.
    :type model: type
    :param runtime: A boolean flag indicating whether this permission is created at runtime. Defaults to False.
    :type runtime: bool, optional
    :param mapper: A callable object used to generate permission strings at runtime. Defaults to None.
    :type mapper: callable, optional
    :param methods: A list of HTTP methods allowed by this permission. Defaults to None.
    :type methods: list, optional
    """

    codename: str
    """A string representing the codename of the permission."""

    name: str
    """A string representing the name of the permission."""

    model: type
    """A Python class representing the model that this permission is associated with."""

    is_runtime: bool
    """A boolean flag indicating whether this permission is created at runtime. Defaults to False."""

    errors = {
        "not-found": {
            "detail": "You don't have enough permissions to access this resource"
        }
    }
    """A dictionary containing error messages raised by the permission."""

    def __init__(
        self,
        codename: str,
        name: str,
        model: type,
        runtime: bool = False,
        mapper=None,
        methods=None,
    ) -> None:
        self.codename = codename
        self.model = model
        self.name = name
        self.methods = methods or []
        self.is_runtime = runtime
        self._permission = None
        self._mapper = mapper or (lambda this, instance: this.codename % instance.pk)

        if not self.is_runtime:
            self._permission = self.create()

    def __call__(self, *args, **kwargs):
        # Note that we need this method as django rest_framework will try to instantiate
        # this object even if it has been instantiated.
        return self

    def __contains__(self, x: str) -> bool:
        for method in self.methods or []:
            if x in method.methods:
                return True
        return False

    def _ensure_table(self) -> bool:
        # WARNING: We have to check that the Permission table exists before
        # we can create our permission objects. Otherwise we would run into
        # errors when running migrate for the first time.
        return "auth_permission" in connection.introspection.table_names()

    def create(self, *args) -> Permission:
        """Create a new permission object with the given codename, name, and model.

        :param args: Optional arguments to substitute into the codename string.
        :type args: Any
        :return: The newly created Permission object.
        :rtype: Permission
        """
        if self._permission and not self.is_runtime:
            return self._permission

        codename = self.codename % args
        name = self.name % args

        if not self._ensure_table():
            return None

        try:
            # Using .get() uses only one database query
            self._permission = Permission.objects.get(codename=codename)
        except (Permission.MultipleObjectsReturned, Permission.DoesNotExist):
            content_type = ContentType.objects.get_for_model(self.model)
            self._permission = Permission.objects.create(
                codename=codename, name=name, content_type=content_type
            )
        return self._permission

    def has_object_permission(self, request, view, obj):
        """Validates whether a user as appropriate rights to access the given object.

        :param request: the HttpRequest
        :type request: Request
        :param view: the api view
        :type view: APIView
        :param obj: the instance a user wants to have access to
        :type obj: ? extends Model
        :raises ValidationError: if the required permission could not be found
        :return: ``False`` if pre-defined requirements could not be satisfied, ``True``
                 otherwise.
        :rtype: bool
        """
        if not isinstance(obj, self.model) or request.method not in self:
            return False

        # Every admin should have access to all resources
        user: User = request.user
        if user.is_staff or user.is_superuser:
            return True

        if user.is_anonymous or not user.is_authenticated:
            return False

        acc = Account.objects.get(user=user)
        if acc.role == Role.ADMIN:
            return True

        permission = self.get(obj)
        if not permission:
            # We have to throw the error here as the original check won't
            # use the False as wrong validation result.
            raise ValidationError(**self.errors["not-found"])

        return permission in request.user.user_permissions.all()

    def get(self, instance) -> Permission:
        """Returns the permission required to access the given object.

        :param instance: the object a user wants to access
        :type instance: ? extends Model
        :return: the required permission
        :rtype: Permission
        """
        permission = self._permission
        if self.is_runtime:
            # runtime permissions may be created multiple times so we have
            # to search for the desired permission
            value = self._mapper(self, instance) if self._mapper else self.codename
            try:
                permission = Permission.objects.get(codename=value)
            except (Permission.DoesNotExist, Permission.MultipleObjectsReturned):
                logger.warning(f"Could not resolve permission: codename='{value}'")
                return None

        return permission

    def assign_to(self, usr: User, *args):
        """Assigns this permission to the given user.

        :param usr: the user that gets this permission
        :type usr: User
        """
        permission = self.create(*args)
        logger.debug(f"Granting permission '{permission.codename}' to {usr.username}")
        usr.user_permissions.add(permission)

    def remove_from(self, usr: User, instance):
        """Removes a specific permission from the given user.

        :param usr: the user
        :type usr: User
        :param instance: the object a user had access to
        :type instance: ? extends Model
        """
        if not isinstance(instance, self.model):
            return

        permission = self.get(instance)
        if permission is not None:
            logger.debug(
                f"Removing permission '{permission.codename}' from {usr.username}"
            )
            usr.user_permissions.remove(permission)


CanEditTeam = BoundPermission(
    "can_edit_team_%s", "Can modify team (%s)", Team, runtime=True, methods=[Patch, Put]
)
CanViewTeam = BoundPermission(
    "can_view_team_%s", "Can view team (%s)", Team, runtime=True, methods=[Get]
)
CanDeleteTeam = BoundPermission(
    "can_delete_team_%s", "Can delete team (%s)", Team, runtime=True, methods=[Delete]
)

# We have to split up both permissions as projects can only be
# removed by their owners or at least users that have a delete
# permission.
CanEditProject = BoundPermission(
    "can_edit_project_%s",
    "Can modify project (%s)",
    Project,
    runtime=True,
    methods=[Get, Patch],
)
CanDeleteProject = BoundPermission(
    "can_delete_project_%s",
    "Can delete project (%s)",
    Project,
    runtime=True,
    methods=[Delete],
)

# The same applies to user permissions. Note that super-users and
# admin users will gain permissions immediately.
CanEditUser = BoundPermission(
    "can_edit_user_%s", "Can modify user (%s)", User, runtime=True, methods=[Get, Patch]
)
CanDeleteUser = BoundPermission(
    "can_delete_user_%s", "Can delete user (%s)", User, runtime=True, methods=[Delete]
)
CanCreateUser = BoundPermission(
    "can_create_user", "Can create users", User, methods=[Post]
)

CanViewAccount = BoundPermission(
    "can_view_acc_%s", "Can view account (%s)", Account, runtime=True, methods=[Get]
)
CanEditAccount = BoundPermission(
    "can_edit_acc_%s", "Can modify account (%s)", Account, runtime=True, methods=[Patch]
)

CanEditBundle = BoundPermission(
    "can_edit_bundle_%s",
    "Can edit bundle (%s)",
    Bundle,
    runtime=True,
    methods=[Patch, Delete],
)
CanDeleteBundle = BoundPermission(
    "can_delete_bundle_%s",
    "Can delete bundle (%s)",
    Bundle,
    runtime=True,
    methods=[Delete],
)
CanViewBundle = BoundPermission(
    "can_view_bundle_%s", "Can view bundle (%s)", Bundle, runtime=True, methods=[Get]
)
