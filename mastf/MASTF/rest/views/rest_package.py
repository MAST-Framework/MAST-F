from rest_framework import permissions

from mastf.MASTF.serializers import PackageSerializer, PackageVulnerabilitySerializer
from mastf.MASTF.models import Package, PackageVulnerability
from mastf.MASTF.forms import PackageForm, PackageVulnerabilityForm

from .base import APIViewBase, ListAPIViewBase, CreationAPIViewBase

__all__ = [
    'PackageView', 'PackageCreationView', 'PackageListView', 
    'PackageVulnerabilityView', 'PackageVulnerabilityCreationView', 
    'PackageVulnerabilityListView', 
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
    
    
