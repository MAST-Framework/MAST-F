from rest_framework import permissions
from django.db import models

from mastf.MASTF.serializers import BundleSerializer
from mastf.MASTF.models import Bundle
from mastf.MASTF.forms import BundleForm
from mastf.MASTF.utils.enum import Visibility
from mastf.MASTF.rest.permissions import IsBundleMember

from .base import CreationAPIViewBase, APIViewBase, ListAPIViewBase

__all__ = [
    'BundleView',
    'BundleCreationView',
    'BundleListView',
]

class BundleView(APIViewBase):
    model = Bundle
    serializer_class = BundleSerializer
    permission_classes = [permissions.IsAuthenticated & IsBundleMember]

class BundleCreationView(CreationAPIViewBase):
    model = Bundle
    form_class = BundleForm
    permission_classes = [permissions.IsAuthenticated & IsBundleMember]

class BundleListView(ListAPIViewBase):
    queryset = Bundle.objects.all()
    serializer_class = BundleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def filter_queryset(self, queryset):
        return Bundle.get_by_owner(self.request.user, queryset)
