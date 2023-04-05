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
        

class CeleryStatusSerializer(serializers.Serializer):
    pending = serializers.BooleanField(default=False, required=False)
    current = serializers.IntegerField(required=True)
    total = serializers.IntegerField(default=100, required=False)
    percent = serializers.FloatField(required=True)
    detail = serializers.CharField(default=None, required=False)
    complete = serializers.BooleanField(default=False, required=False)
    

class CeleryResultSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)
    state = serializers.CharField(required=True)
    status = CeleryStatusSerializer(required=True)
    
    @staticmethod
    def empty() -> dict:
        # This method should be called whenever the celery worker has not been 
        # started and a scan should be done
        return {
            "state": "PENDING",
            "status": {
                "pending": True, "detail": "Celery Worker not started"
            }
        }
