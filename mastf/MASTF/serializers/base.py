from django.contrib.auth.models import User
from rest_framework import serializers

from mastf.MASTF.models import (
    Project,
    Team,
)

__all__ = [
    'UserSerializer', 'TeamSerializer', 'ProjectSerializer',
    'ManyToManyField',
    'ManyToManySerializer',
]

class ManyToManyField(serializers.Field):
    def __init__(self, to, field_name: str = 'pk', **kwargs):
        super().__init__(**kwargs)
        self.model = to
        self.field_name = field_name

    def to_internal_value(self, data: str):
        values = str(data).split(',') if not isinstance(data, (list, tuple)) else values

        elements = []
        for objid in values:
            if isinstance(objid, self.model):
                elements.append(objid)
                continue

            query = self.model.objects.filter(**{self.field_name: objid})
            if query.exists():
                elements.append(query.first())

        return elements

    def to_representation(self, value: list):
        if isinstance(value, str) or not value:
            return str(value)

        return ','.join([str(x.pk) for x in value])

class ManyToManySerializer(serializers.ModelSerializer):
    rel_fields = None

    def update(self, instance, validated_data):
        if self.rel_fields and isinstance(self.rel_fields, (list, tuple)):
            for field_name in self.rel_fields:
                if not hasattr(instance, field_name) or field_name not in validated_data:
                    continue
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
