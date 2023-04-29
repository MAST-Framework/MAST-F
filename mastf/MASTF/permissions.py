import logging

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission, User

from rest_framework.permissions import (
    BasePermission, SAFE_METHODS, OperationHolderMixin
)
from rest_framework.exceptions import ValidationError

from mastf.MASTF.models import (
    Team,
    Project,
    Bundle
)


logger = logging.getLogger(__name__)

# TODO:(documentation)
class _Method(OperationHolderMixin, BasePermission):

    def __init__(self, *args) -> None:
        self.methods = list(args) or SAFE_METHODS

    def __call__(self, *args, **kwargs):
        # same as defined in BoundPermission, we have to define
        # this object to be callable to prevent errors.
        return self

    def __repr__(self) -> str:
        return str(self.methods)

    def has_permission(self, request, view):
        return request.method in self.methods

Delete = _Method('DELETE')
Post = _Method('POST')
Patch = _Method('PATCH')
Get = _Method('GET')
Put = _Method('PUT')

# TODO:(documentation)
class BoundPermission(OperationHolderMixin, BasePermission):
    codename: str
    name: str
    model: type
    is_runtime: bool

    errors = {
        'not-found': {'detail': "You don't have enough permissions to access this resource"}
    }

    def __init__(self, codename: str, name: str, model: type,
                 runtime: bool = False, mapper=None, methods=None) -> None:
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
        for method in (self.methods or []):
            if x in method.methods:
                return True
        return False

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
        permission = Permission.objects.filter(codename=codename)
        if permission.exists():
            self._permission = permission
        else:
            content_type = ContentType.objects.get_for_model(self.model)
            self._permission = Permission.objects.create(
                codename=codename,
                name=self.name,
                content_type=content_type
            )
        return self._permission

    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, self.model) or request.method not in self:
            return False

        permission = self.get(obj)
        if not permission:
            # We have to throw the error here as the original check won't
            # use the False as wrong validation result.
            raise ValidationError(**self.errors['not-found'])

        return permission in request.user.user_permissions.all()

    def get(self, instance) -> Permission:
        permission = self._permission
        if self.is_runtime:
            # runtime permissions may be created multiple times so we have
            # to search for the desired permission
            value = self._mapper(self, instance) if self._mapper else self.codename

            permission = Permission.objects.filter(codename=value)
            if not permission.exists():
                logger.warning(f"Could not resolve permission: codename='{value}'")
                return None
            permission = permission.first()

        return permission

    def assign_to(self, usr: User, *args):
        permission = self.create(*args)
        logging.debug(f"Granting permission '{permission.codename}' to {usr.username}")
        usr.user_permissions.add(permission)

    def remove_from(self, usr: User, instance):
        if not isinstance(instance, self.model):
            return

        permission = self.get(instance)
        if permission is not None:
            logging.debug(f"Removing permission '{permission.codename}' from {usr.username}")
            usr.user_permissions.remove(permission)




CanEditTeam = BoundPermission("can_edit_team_%s", "Can modify teams", Team, runtime=True, methods=[Get, Patch])

# We have to split up both permissions as projects can only be
# removed by their owners or at least users that have a delete
# permission.
CanEditProject = BoundPermission("can_edit_project_%s", "Can modify project", Project, runtime=True, methods=[Get, Patch])
CanDeleteProject = BoundPermission("can_delete_project_%s", "Can delete project", Project, runtime=True, methods=[Delete])

# The same applies to user permissions. Note that super-users and
# admin users will gain permissions immediately.
CanEditUser = BoundPermission("can_edit_user_%s", "Can modify user", User, runtime=True, methods=[Get, Patch])
CanDeleteUser = BoundPermission("can_delete_user_%s", "Can delete user", User, runtime=True, methods=[Delete])
CanCreateUser = BoundPermission("can_create_user", "Can create users", User, methods=[Post])

CanEditBundle = BoundPermission("can_edit_bundle_%s", "Can edit bundles", Bundle, runtime=True)
CanDeleteBundle = BoundPermission("can_delete_bundle_%s", "Can delete bundles", Bundle, runtime=True)
CanViewBundle = BoundPermission("can_view_bundle_%s", "Can view bundles", Bundle, runtime=True)

