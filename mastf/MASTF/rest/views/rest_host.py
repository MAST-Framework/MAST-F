from rest_framework import permissions

from mastf.MASTF.models import (
    Host,
    DataCollectionGroup,
    CipherSuite,
    TLS,
    Scan,
    HostTemplate
)
from mastf.MASTF.serializers import (
    HostSerializer,
    DataCollectionGroupSerializer,
    CipherSuiteSerializer,
    TLSSerializer,
    HostTemplateSerializer
)
from mastf.MASTF.forms import (
    HostForm,
    DataCollectionGroupForm,
    CipherSuiteForm,
    TLSForm,
    HostTemplateForm
)
from mastf.MASTF.rest.permissions import CanEditScanAsField, CanEditScan, IsExternal

from .base import APIViewBase, CreationAPIViewBase, ListAPIViewBase, GetObjectMixin

__all__ = [
    'HostView',
    'HostCreationView',
    'HostListView',
    'TLSView',
    'TLSCreationView',
    'TLSListView',
    'CipherSuiteView',
    'CipherSuiteCreationView',
    'CipherSuiteListView',
    'DataCollectionGroupView',
    'DataCollectionGroupCreationView',
    'DataCollectionGroupListView',
    'HostTemplateView',
    'HostTemplateCreationView',
    'HostTemplateListView',
]

## Implementation
########################################################################
# HOST
########################################################################
class HostView(APIViewBase):
    model = Host
    serializer_class = HostSerializer
    permission_classes = [permissions.IsAuthenticated & CanEditScanAsField]

class HostCreationView(CreationAPIViewBase):
    model = Host
    form_class = HostForm
    permission_classes = [permissions.IsAuthenticated & CanEditScanAsField]

    def make_uuid(self):
        return f"hst_{super().make_uuid()}"

# route /scan/..../hosts
class HostListView(GetObjectMixin, ListAPIViewBase):
    queryset = Host.objects.all()
    model = Scan
    lookup_field = 'scan_uuid'
    serializer_class = HostSerializer
    permission_classes = [permissions.IsAuthenticated & CanEditScan]

    def filter_queryset(self, queryset):
        return queryset.filter(scan=self.get_object())

class HostRelListView(GetObjectMixin, ListAPIViewBase):
    permission_classes = [permissions.IsAuthenticated & CanEditScanAsField]
    model = Host

    def filter_queryset(self, queryset):
        return queryset.filter(hosts__scan=self.get_object())

########################################################################
# HOST-TEMPLATE
########################################################################
class HostTemplateView(APIViewBase):
    model = HostTemplate
    serializer_class = HostTemplateSerializer
    permission_classes = [permissions.IsAuthenticated & ~IsExternal]

class HostTemplateCreationView(CreationAPIViewBase):
    model = HostTemplate
    form_class = HostTemplateForm
    permission_classes = [permissions.IsAuthenticated]

class HostTemplateListView(ListAPIViewBase):
    queryset = HostTemplate.objects.all()
    serializer_class = HostTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]

########################################################################
# TLS
########################################################################
class TLSView(APIViewBase):
    permission_classes = [permissions.IsAuthenticated]
    model = TLS
    serializer_class = TLSSerializer

class TLSCreationView(CreationAPIViewBase):
    permission_classes = [permissions.IsAuthenticated]
    model = TLS
    form_class = TLSForm

class TLSListView(HostRelListView):
    serializer_class = TLSSerializer
    queryset = TLS.objects.all()

########################################################################
# CipherSUite
########################################################################
class CipherSuiteView(APIViewBase):
    permission_classes = [permissions.IsAuthenticated]
    model = CipherSuite
    serializer_class = CipherSuiteSerializer

class CipherSuiteCreationView(CreationAPIViewBase):
    permission_classes = [permissions.IsAuthenticated]
    model = CipherSuite
    form_class = CipherSuiteForm

class CipherSuiteListView(HostRelListView):
    serializer_class = CipherSuiteSerializer
    queryset = CipherSuite.objects.all()

########################################################################
# DataCollectionGroup
########################################################################
class DataCollectionGroupView(APIViewBase):
    permission_classes = [permissions.IsAuthenticated]
    model = DataCollectionGroup
    serializer_class = DataCollectionGroupSerializer

class DataCollectionGroupCreationView(CreationAPIViewBase):
    permission_classes = [permissions.IsAuthenticated]
    model = DataCollectionGroup
    form_class = DataCollectionGroupForm

class DataCollectionGroupListView(HostRelListView):
    serializer_class = DataCollectionGroupSerializer
    queryset = DataCollectionGroup.objects.all()