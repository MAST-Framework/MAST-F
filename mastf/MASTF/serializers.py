from rest_framework import serializers

from mastf.MASTF.models import *


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'

