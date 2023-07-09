import os
import logging
import pathlib

from uuid import UUID

from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import BaseRenderer
from rest_framework.response import Response
from rest_framework import status, views, exceptions
from rest_framework.authentication import (
    TokenAuthentication,
    BasicAuthentication,
    SessionAuthentication,
)

from django.shortcuts import get_object_or_404
from django.db.models import QuerySet
from django.contrib import messages

from celery.result import AsyncResult

from mastf.MASTF.serializers import (
    ScanSerializer,
    CeleryAsyncResultSerializer,
    ScanTaskSerializer,
)
from mastf.MASTF.models import (
    Scan,
    Details,
    ScanTask,
    Scanner,
)
from mastf.MASTF.forms import ScanForm
from mastf.MASTF.rest.permissions import ReadOnly, CanEditScan
from mastf.MASTF.scanners.plugin import ScannerPlugin
from mastf.MASTF.utils.upload import handle_scan_file_upload
from mastf.MASTF import tasks
from mastf.MASTF.permissions import Get

from .base import APIViewBase, ListAPIViewBase, CreationAPIViewBase, GetObjectMixin

logger = logging.getLogger(__name__)

__all__ = ["AppIconView", "ImageRenderer"]

class ImageRenderer(BaseRenderer):
    media_type = "image/*"
    format = "png"
    charset = None
    render_style = "binary"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data

class AppIconView(GetObjectMixin, views.APIView):
    model = Scan
    lookup_field = "scan_uuid"
    authentication_classes = [
        BasicAuthentication,
        SessionAuthentication,
        TokenAuthentication,
    ]
    permission_classes = [IsAuthenticated & CanEditScan]
    renderer_classes = [ImageRenderer]

    def get(self, request, *args, **kwargs) -> Response:
        scan: Scan = self.get_object()
        details = Details.objects.get(scan=scan)

        path = pathlib.Path(str(details.icon))
        if not path.exists():
            return Response(status=status.HTTP_404_NOT_FOUND)

        with open(str(path), "rb") as fp:
            data = fp.read()

        return Response(data, content_type="image/png")