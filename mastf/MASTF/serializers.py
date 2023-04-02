from django.contrib.auth.models import User
from rest_framework import serializers

from mastf.MASTF.models import (
    Project, 
    FindingTemplate,
    AppPermission,
    Scan,
    Finding
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username', 'email', 'groups', 'date_joined',
            'user_permissions'
        ]
        
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
        
        
class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FindingTemplate
        fields = '__all__'


class AppPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppPermission
        fields = '__all__'


class ScanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scan
        fields = '__all__'

class FindingSerializer(serializers.ModelSerializer):
    template = ScanSerializer(many=False)
    
    class Meta:
        model = Finding
        fields = '__all__'