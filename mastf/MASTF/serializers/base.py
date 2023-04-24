import logging

from django.contrib.auth.models import User
from django.db.models import Manager
from rest_framework import serializers

from mastf.MASTF.models import (
    Project,
    Team,
    Bundle,
)

__all__ = [
    'UserSerializer',
    'TeamSerializer',
    'ProjectSerializer',
    'ManyToManyField',
    'ManyToManySerializer',
    'BundleSerializer'
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

    def __init__(self, model, field_name='pk', delimiter: str = ',',
                 mapper=None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.model = model
        self.delimiter = delimiter or ','
        self.field_name = field_name
        self.converter = mapper or str

    def to_internal_value(self, data: str):
        """Transform the *incoming* primitive data into a native value."""
        values = (str(data).split(self.delimiter)
            if not isinstance(data, (list, tuple))
            else values
        )

        elements = []
        for objid in values:
            if isinstance(objid, self.model):
                elements.append(objid)
                continue

            element_id = objid if not self.converter else self.converter(objid)
            query = self.model.objects.filter(**{self.field_name: element_id})
            if query.exists():
                elements.append(query.first())
            else:
                logger.debug(f'Could not resolve objID: "{objid}" and name: "{self.field_name}"')

        return elements

    def to_representation(self, value: list):
        """Transform the *outgoing* native value into primitive data."""
        if isinstance(value, str) or not value:
            return str(value)

        if isinstance(value, Manager):
            value = value.all()

        key = self.field_name or 'pk'
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
    """

    rel_fields = None
    """The fields related to a many-to-many relationship."""

    def update(self, instance, validated_data):
        if self.rel_fields and isinstance(self.rel_fields, (list, tuple)):
            for field_name in self.rel_fields:
                if not hasattr(instance, field_name) or field_name not in validated_data:
                    logger.debug('[SER] Could not find field ("%s") in class: "%s"',
                                 field_name, self.__class__)
                    continue
                # Many-To-Many relationships are represented by a Manager
                # instance internally.
                manager = getattr(instance, field_name)
                manager.add(validated_data.pop(field_name))

        return super().update(instance, validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username', 'email', 'groups', 'date_joined',
            'user_permissions'
        ]


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    owner = UserSerializer(many=False)
    team = TeamSerializer(many=False)

    class Meta:
        model = Project
        fields = '__all__'


class BundleSerializer(ManyToManySerializer):
    rel_fields = ['projects']
    projects = ManyToManyField(Project)

    class Meta:
        model = Bundle
        fields = '__all__'
