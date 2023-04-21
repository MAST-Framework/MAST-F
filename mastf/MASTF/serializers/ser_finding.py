from rest_framework import serializers

from mastf.MASTF.models import (
    FindingTemplate,
    AppPermission,
    Package,
    PackageVulnerability,
    Dependency,
    Finding,
    Vulnerability,
    Snippet,
    Hosts,
)

__all__ = [
    'TemplateSerializer',
    'AppPermissionSerializer',
    'SnippetSerializer',
    'FindingSerializer',
    'VulnerabilitySerializer',
    'PackageSerializer',
    'PackageVulnerabilitySerializer',
    'DependencySerializer',
    'HostsSerializer',
]


class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FindingTemplate
        fields = '__all__'


class AppPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppPermission
        fields = '__all__'
    
class HostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hosts
        fields = '__all__'

class SnippetSerializer(serializers.ModelSerializer):

    class Meta:
        model = Snippet
        exclude = ['sys_path']


class FindingSerializer(serializers.ModelSerializer):
    template = TemplateSerializer(many=False)
    snippet = SnippetSerializer(many=False)

    class Meta:
        model = Finding
        fields = '__all__'


class VulnerabilitySerializer(serializers.ModelSerializer):
    template = TemplateSerializer(many=False)
    snippet = SnippetSerializer(many=False)

    class Meta:
        model = Vulnerability
        fields = '__all__'


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = '__all__'


class PackageVulnerabilitySerializer(serializers.ModelSerializer):
    package = PackageSerializer(many=False)

    class Meta:
        model = PackageVulnerability
        fields = '__all__'


class DependencySerializer(serializers.ModelSerializer):
    package = PackageSerializer(many=False)

    class Meta:
        model = Dependency
        fields = '__all__'
