from uuid import uuid4
import json

from django.core import serializers
from django.http import HttpResponse
from django.http import Http404

from rest_framework import permissions, views
from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework.request import Request

from mastf.MASTF.serializers import AppPermissionSerializer
from mastf.MASTF.models import AppPermission
from mastf.MASTF.forms import AppPermissionForm

from .base import APIViewBase, ListAPIViewBase, CreationAPIViewBase

__all__ = [
    'AppPermissionView', 'AppPermissionCreationView', 'AppPermissionListView', 'AppPermissionFileUpload',
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


class AppPermissionFileUpload(APIView):

    model = AppPermission
    def post(self, request: Request) -> Response:
        if request.FILES != None:
            HttpResponse("File received")
        else: HttpResponse("File not received")