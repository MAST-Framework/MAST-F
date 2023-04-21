from uuid import uuid4
import json

from django.core import serializers
from django.http import HttpResponse
from django.http import Http404

from rest_framework import permissions, views

from mastf.MASTF.serializers import AppPermissionSerializer
from mastf.MASTF.models import AppPermission
from mastf.MASTF.forms import AppPermissionForm

from .base import APIViewBase, ListAPIViewBase, CreationAPIViewBase

__all__ = [
    'AppPermissionView', 'AppPermissionCreationView', 'AppPermissionListView',
]

class AppPermissionView(APIViewBase):
    """Basic API-Endpoint to update, delete and fetch app permissions"""

    permission_classes = [permissions.IsAuthenticated]
    model = AppPermission
    serializer_class = AppPermissionSerializer
    lookup_field = 'permission_uuid'


class AppPermissionCreationView(CreationAPIViewBase):

    permission_classes = [permissions.IsAuthenticated]
    model = AppPermission
    form_class = AppPermissionForm


class AppPermissionListView(ListAPIViewBase):

    queryset = AppPermission.objects.all()
    serializer_class = AppPermissionSerializer
    permission_classes = [permissions.IsAuthenticated]


"""def AppPermissionListRangeView(request):
    get = request.GET
    if "start" not in get or "end" not in get:
        raise Http404
    queryset = AppPermission.objects.all().order_by("name")
    start = int(get["start"])
    end = int(get["end"])
    if end >= len(queryset):
        end = len(queryset)
    if start >= end:
        raise Http404
    re = serializers.serialize("json", queryset[start:end])
    return HttpResponse(re, content_type='application/json')"""