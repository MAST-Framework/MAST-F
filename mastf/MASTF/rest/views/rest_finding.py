from uuid import uuid4

from rest_framework import permissions

from mastf.MASTF.serializers import FindingSerializer, VulnerabilitySerializer
from mastf.MASTF.models import Finding, Vulnerability, Scanner, Scan, FindingTemplate
from mastf.MASTF.forms import FindingForm, VulnerabilityForm

from mastf.MASTF.rest.permissions import IsScanInitiator

from .base import APIViewBase, CreationAPIViewBase, ListAPIViewBase

__all__ = [
    'FindingView', 'FindingCreationView', 'FindingListView', 
    'VulnerabilityView', 'VulnerabilityCreationView', 'VulnerabilityListView'
]

class FindingView(APIViewBase):
    permission_classes = [permissions.IsAuthenticated]
    model = Finding
    lookup_field = 'finding_id'
    serializer_class = FindingSerializer
    
class FindingCreationView(CreationAPIViewBase):
    permission_classes = [permissions.IsAuthenticated & IsScanInitiator]
    model = Finding
    form_class = FindingForm
    
    def set_defaults(self, request, data: dict) -> None:
        data['scan'] = Scan.objects.get(scan_uuid=data['scan'])
        self.check_object_permissions(self.request, data['scan'])
        
        data['template'] = Scan.objects.get(template_id=data['template'])
        data['scanner'] = Scanner.objects.get(name=data['scanner'], project=data['scan'].project)
    
    
    def make_uuid(self):
        return f"SF-{uuid4()}-{uuid4()}"
    
class FindingListView(ListAPIViewBase):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Finding.objects.all()
    serializer_class = FindingSerializer
    
    def filter_queryset(self, queryset):
        return queryset.filter(scan__initiator=self.request.user)
    
##############################################################################
# Vulnerability
##############################################################################
class VulnerabilityView(APIViewBase):
    permission_classes = [permissions.IsAuthenticated]
    model = Vulnerability
    lookup_field = 'finding_id'
    serializer_class = VulnerabilitySerializer
    
class VulnerabilityCreationView(CreationAPIViewBase):
    permission_classes = [permissions.IsAuthenticated & IsScanInitiator]
    model = Vulnerability
    form_class = VulnerabilityForm
    
    def set_defaults(self, request, data: dict) -> None:
        data['scan'] = Scan.objects.get(scan_uuid=data['scan'])
        self.check_object_permissions(self.request, data['scan'])
        
        data['template'] = Scan.objects.get(template_id=data['template'])
        data['scanner'] = Scanner.objects.get(name=data['scanner'], project=data['scan'].project)
    
    def make_uuid(self):
        return f"SV-{uuid4()}-{uuid4()}"
    
class VulnerabilityListView(ListAPIViewBase):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Vulnerability.objects.all()
    serializer_class = VulnerabilitySerializer
    
    def filter_queryset(self, queryset):
        return queryset.filter(scan__initiator=self.request.user)
    
