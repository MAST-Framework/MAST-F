from rest_framework import permissions
from django.shortcuts import get_object_or_404

from mastf.MASTF.serializers import (
    PackageSerializer,
    PackageVulnerabilitySerializer,
    DependencySerializer
)
from mastf.MASTF.models import (
    Package,
    PackageVulnerability,
    Dependency,
    Project
)
from mastf.MASTF.forms import (
    PackageForm,
    PackageVulnerabilityForm,
    DependencyForm

)
from mastf.MASTF.rest.permissions import IsScanProjectMember, CanEditProject

from .base import APIViewBase, ListAPIViewBase, CreationAPIViewBase

__all__ = [
    'PackageView',
    'PackageCreationView',
    'PackageListView',
    'PackageVulnerabilityView',
    'PackageVulnerabilityCreationView',
    'PackageVulnerabilityListView',
    'DependencyView',
    'DependencyListView',
    'DependencyCreationView',
]


class PackageView(APIViewBase):
    model = Package
    serializer_class = PackageSerializer
    permission_classes = [permissions.IsAuthenticated]

class PackageCreationView(CreationAPIViewBase):
    model = Package
    form_class = PackageForm
    permission_classes = [permissions.IsAuthenticated]

class PackageListView(ListAPIViewBase):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Package.objects.all()
    serializer_class = PackageSerializer


# PackageVulnerability
class PackageVulnerabilityView(APIViewBase):
    model = PackageVulnerability
    serializer_class = PackageVulnerabilitySerializer
    permission_classes = [permissions.IsAuthenticated]

class PackageVulnerabilityCreationView(CreationAPIViewBase):
    model = PackageVulnerability
    form_class = PackageVulnerabilityForm
    permission_classes = [permissions.IsAuthenticated]

class PackageVulnerabilityListView(ListAPIViewBase):
    permission_classes = [permissions.IsAuthenticated]
    queryset = PackageVulnerability.objects.all()
    serializer_class = PackageVulnerabilitySerializer

# Dependencies
class DependencyView(APIViewBase):
    model = Dependency
    serializer_class = DependencySerializer
    permission_classes = [permissions.IsAuthenticated & IsScanProjectMember]

class DependencyListView(ListAPIViewBase):
    queryset = Dependency.objects.all()
    serializer_class = DependencySerializer
    can_edit_permission = IsScanProjectMember

    def filter_queryset(self, queryset):
        project_uuid = self.request.GET.get('project', None)
        if project_uuid:
            # The GET parameter can be set to list permissions according to the
            # selected project
            project = get_object_or_404(Project.objects.all(), pk=project_uuid)
            return queryset.filter(project=project)

        return [x for x in super().filter_queryset(queryset)
                if self.can_edit_permission.has_object_permission(self.request, self, x)]

class DependencyCreationView(CreationAPIViewBase):
    model = Dependency
    permission_classes = [permissions.IsAuthenticated & CanEditProject]
    form_class = DependencyForm

    def make_uuid(self):
        return f"{super().make_uuid()}{super().make_uuid()}"

    def set_defaults(self, request, data: dict) -> None:
        # Check object permissions to create a new dependency
        self.check_object_permissions(request, data['project'])
