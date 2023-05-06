from uuid import uuid4

from rest_framework import permissions

from mastf.MASTF.serializers import FindingSerializer, VulnerabilitySerializer
from mastf.MASTF.models import Finding, Vulnerability, Scanner, Scan, FindingTemplate
from mastf.MASTF.forms import FindingForm, VulnerabilityForm

from mastf.MASTF.rest.permissions import IsScanInitiator, CanEditScanAsField, CanEditScan

from .base import APIViewBase, CreationAPIViewBase, ListAPIViewBase, GetObjectMixin

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
        self.check_object_permissions(self.request, data['scan'])

    def make_uuid(self):
        return f"SF-{uuid4()}-{uuid4()}"

class FindingListView(GetObjectMixin, ListAPIViewBase):
    permission_classes = [permissions.IsAuthenticated & CanEditScan]
    queryset = Finding.objects.all()
    serializer_class = FindingSerializer
    model = Scan
    lookup_field = 'scan_uuid'

    def filter_queryset(self, queryset):
        return queryset.filter(scan=self.get_object())

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
        self.check_object_permissions(self.request, data['scan'])

    def make_uuid(self):
        return f"SV-{uuid4()}-{uuid4()}"

class VulnerabilityListView(GetObjectMixin, ListAPIViewBase):
    permission_classes = [permissions.IsAuthenticated & CanEditScan]
    queryset = Vulnerability.objects.all()
    serializer_class = VulnerabilitySerializer
    model = Scan
    lookup_field = 'scan_uuid'

    def filter_queryset(self, queryset):
        return queryset.filter(scan=self.get_object())

