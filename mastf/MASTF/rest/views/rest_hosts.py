from mastf.MASTF.models import Hosts

from django.http import HttpResponse
from django.http import Http404

from mastf.MASTF.models import Hosts
from mastf.MASTF.forms import HostForm
from mastf.MASTF.serializers import HostsSerializer

from rest_framework import permissions

from .base import APIViewBase, ListAPIViewBase, CreationAPIViewBase

__all__ = ['HostCreationView', 'HostsListView', 'HostView']

class HostCreationView(CreationAPIViewBase):

    form_class = HostForm
    model = Hosts
    permission_classes = [permissions.IsAuthenticated]

class HostsListView(ListAPIViewBase):
    queryset = Hosts.objects.all()
    serializer_class = HostsSerializer
    permission_classes = [permissions.IsAuthenticated]

class HostView(APIViewBase):
    permission_classes = [permissions.IsAuthenticated]
    model = Hosts
    serializer_class = HostsSerializer
    lookup_field = "host_uuid"