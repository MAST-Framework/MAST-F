from rest_framework import permissions

from mastf.MASTF.models import (
    Host,
    ConnectionInfo,
    DataCollectionGroup,
    CipherSuite,
    TLS,
    Scan
)
from mastf.MASTF.serializers import (
    HostSerializer,
    ConnectionSerializer,
    DataCollectionGroupSerializer,
    CipherSuiteSerializer,
    TLSSerializer
)
from mastf.MASTF.forms import (
    HostForm,
    ConnectionForm,
    DataCollectionGroupForm,
    CipherSuiteForm,
    TLSForm
)
from mastf.MASTF.rest.permissions import CanEditScanAsField, CanEditScan

from .base import APIViewBase, CreationAPIViewBase, ListAPIViewBase, GetObjectMixin

__all__ = [
    'HostView',
    'HostCreationView',
    'HostListView',
    'ConnectionInfoView',
    'ConnectionInfoCreationView',
    'ConnectionInfoListView',
    'TLSView',
    'TLSCreationView',
    'TLSListView',
    'CipherSuiteView',
    'CipherSuiteCreationView',
    'CipherSuiteListView',
    'DataCollectionGroupView',
    'DataCollectionGroupCreationView',
    'DataCollectionGroupListView',
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
# Connection
########################################################################
class ConnectionInfoView(APIViewBase):
    permission_classes = [permissions.IsAuthenticated]
    model = ConnectionInfo
    serializer_class = ConnectionSerializer

class ConnectionInfoCreationView(CreationAPIViewBase):
    permission_classes = [permissions.IsAuthenticated]
    model = ConnectionInfo
    form_class = ConnectionForm

class ConnectionInfoListView(HostRelListView):
    serializer_class = ConnectionSerializer
    queryset = ConnectionInfo.objects.all()

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