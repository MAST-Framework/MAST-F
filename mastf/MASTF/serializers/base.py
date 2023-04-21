from django.contrib.auth.models import User
from rest_framework import serializers

from mastf.MASTF.models import (
    Project,
    Team,
    AppPermission,
)

__all__ = [
    'UserSerializer', 'TeamSerializer', 'ProjectSerializer',
]

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
