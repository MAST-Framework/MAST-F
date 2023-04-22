from rest_framework import permissions

from mastf.MASTF.models import Component
from mastf.MASTF.serializers import ComponentSerializer
from mastf.MASTF.forms import ComponentForm

from mastf.MASTF.rest.permissions import CanEditScanFromScanner, CanEditScan

from .base import (
    CreationAPIViewBase,
    APIViewBase,
    ListAPIViewBase,
    GetObjectMixin
)

__all__ = [
    'ComponentView',
    'ComponentListView',
    'ComponentCreationView',
]

class ComponentView(APIViewBase):
    model = Component
    serializer_class = ComponentSerializer
    permission_classes = [permissions.IsAuthenticated & CanEditScanFromScanner]


class ComponentListView(GetObjectMixin, ListAPIViewBase):
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer
    permission_classes = [permissions.IsAuthenticated & CanEditScan]

    def filter_queryset(self, queryset):
        return queryset.filter(scanner__scan=self.get_object())


class ComponentCreationView(CreationAPIViewBase):
    model = Component
    form_class = ComponentForm
    # The access to a selected scan will be checked when
    # form.is_valid() is executed.
    permission_classes = [permissions.IsAuthenticated]

    def make_uuid(self):
        return f"cpt_{super().make_uuid()}"
