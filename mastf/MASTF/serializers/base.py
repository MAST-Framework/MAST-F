# This file is part of MAST-F's Frontend API
# Copyright (C) 2023  MatrixEditor, Janbehere1
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
import logging

from django.contrib.auth.models import User, Permission
from django.db.models import Manager

from rest_framework import serializers
from rest_framework.fields import empty

from mastf.MASTF.permissions import BoundPermission, CanEditTeam
from mastf.MASTF.models import Project, Team, Bundle, Account, Environment

__all__ = [
    "UserSerializer",
    "TeamSerializer",
    "ProjectSerializer",
    "ManyToManyField",
    "ManyToManySerializer",
    "BundleSerializer",
    "AccountSerializer",
    "EnvironmentSerializer",
]

logger = logging.getLogger(__name__)


class ManyToManyField(serializers.Field):
    """Implementation of a Many-To-Many relation for REST-Framework serializers.

    As described in the ``ManyToManyField`` class for Django forms, the
    behaviour of this almost the same. It will convert multiple database
    objects by placing their primary key (or specified field name) and de-
    serialize JSON lists or strings into qualified database model objects.

    .. code-block:: python

        class AuthorSerializer(serializers.Serializer):
            books = ManyToManySerializer(Book, mapper=int)

    In this example, we have defined a simple serializer that will convert a
    list of ``Book`` objects into JSON and vice versa. Note that mapper argument
    that is necessary if the primary key is of type ``int``.

    .. warning::
        The validated data returned by this field is a tuple that stores the
        retrieved elements and whether they should be replaced with the current
        database values or should be added. Therefore you can add a special
        keyword to the start of the transmitted data:

        .. code-block:: python
            :linenos:

            data = {
                "field_name": [
                    # Indicates the following values will replace any existing values;
                    # leave that value out if you want to add objects to existing values.
                    "$set",
                    "pk1",
                    "pk2", ...
                ]
            }

    :param model: The Django model class
    :type model: class<? extends ``Model``>
    :param delimiter: The string delimiter to use when splitting the
                      input string
    :type delimiter: str
    :param field_name: The field name to query
    :type field_name: str
    :param mapper: A conversion function to optionally convert input keys
    :type mapper: Callable[T, [str]]
    """

    def __init__(
        self, model, field_name="pk", delimiter: str = ",", mapper=None, **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.model = model
        self.delimiter = delimiter or ","
        self.pk_name = field_name or "pk"
        self.converter = mapper or str

    def to_internal_value(self, data: str) -> tuple:
        """Transform the *incoming* primitive data into a native value."""
        values = (
            str(data).split(self.delimiter)
            if not isinstance(data, (list, tuple))
            else data
        )

        elements = []
        append = True
        for objid in values:
            if isinstance(objid, self.model):
                elements.append(objid)
                continue

            if objid == "$set":
                append = False

            element_id = objid if not self.converter else self.converter(objid)
            query = self.model.objects.filter(**{self.pk_name: element_id})
            if query.exists():
                elements.append(query.first())
            else:
                logger.debug(
                    f'Could not resolve objID: "{objid}" and name: "{self.field_name}"'
                )

        return elements, append

    def to_representation(self, value: list):
        """Transform the *outgoing* native value into primitive data."""
        if isinstance(value, str) or not value:
            return str(value)

        if isinstance(value, Manager):
            value = value.all()

        key = self.pk_name or "pk"
        return [str(getattr(x, key)) for x in value]


class ManyToManySerializer(serializers.ModelSerializer):
    """Helper class to simplify updating Many-To-Many relationships.

    This class is an extended version of a ``ModelSerializer`` and should only
    be used on serializer classes that use ``ManyToManyField`` definitions. It
    implements the ``update()`` function which adds selected objects to a
    many-to-many relationship.

    In order to achieve a flawless update, the ``rel_fields`` must contain all
    field names that are related to many-to-many relationships:

    .. code-block:: python

        class AuthorSerializer(ManyToManySerializer):
            rel_fields = ("books",)
            books = ManyToManyField(Book, mapper=int)

            class Meta: # don't forget to specify the model
                model = Author
                fields = '__all__'
    """

    rel_fields = None
    """The fields related to a many-to-many relationship."""

    bound_permissions = None

    def update(self, instance, validated_data):
        if self.rel_fields and isinstance(self.rel_fields, (list, tuple)):
            for field_name in self.rel_fields:
                if field_name not in validated_data:
                    continue
                try:
                    # Many-To-Many relationships are represented by a Manager
                    # instance internally.
                    manager = getattr(instance, field_name)
                    elements, append = validated_data.pop(field_name)
                    if append:
                        manager.add(*elements)
                    else:
                        self._remove_permissions(instance, manager, elements)
                        manager.set(*elements)
                except KeyError:
                    logger.debug(
                        '(%s) Could not find field ("%s") in class: "%s"',
                        self.__class__,
                        field_name,
                        instance.__class__,
                    )

        return super().update(instance, validated_data)

    def _remove_permissions(self, instance, manager, elements):
        current = manager.all()
        diff = set(current) - set(elements)

        for permission in self.bound_permissions or []:
            assert isinstance(
                permission, BoundPermission
            ), f"The given permission object must be a BoundPermission! (Got: {permission})"
            for element in diff:
                # Currently only user elements will be affected from this change
                if isinstance(element, User):
                    permission.remove_from(element, instance)


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "groups", "date_joined", "user_permissions"]


class TeamSerializer(ManyToManySerializer):
    rel_fields = ["users"]
    users = ManyToManyField(User)

    class Meta:
        model = Team
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"


class BundleSerializer(ManyToManySerializer):
    rel_fields = ["projects"]
    projects = ManyToManyField(Project)
    bound_permissions = [CanEditTeam]

    class Meta:
        model = Bundle
        fields = "__all__"


class AccountSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)

    class Meta:
        model = Account
        fields = "__all__"


class EnvironmentSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Environment
