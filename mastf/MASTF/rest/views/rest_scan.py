from uuid import UUID

from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status, views
from rest_framework.authentication import (
    TokenAuthentication,
    BasicAuthentication,
    SessionAuthentication
)

from django.shortcuts import get_object_or_404
from django.http import Http404
from django.db.models import QuerySet

from mastf.MASTF.serializers import ScanSerializer
from mastf.MASTF.models import Scan, Project
from mastf.MASTF.forms import ScanForm
from mastf.MASTF.rest.permissions import ReadOnly, IsScanInitiator

from mastf.MASTF.scanners.plugin import ScannerPlugin

from .base import APIViewBase, ListAPIViewBase, CreationAPIViewBase

__all__ = [
    'ScanView', 'ScanCreationView', 'ScanListView',
    'ScannerView'
]

class ScanView(APIViewBase):
    permission_classes = [IsAuthenticated & (IsScanInitiator | ReadOnly)]
    model = Scan
    serializer_class = ScanSerializer
    lookup_field = 'scan_uuid'


class ScanCreationView(CreationAPIViewBase):
    form_class = ScanForm
    model = Scan

    permission_classes = [IsAuthenticated]

    def set_defaults(self, request, data: dict) -> None:
        project_id = data.pop('project', None)
        if not project_id:
            raise Http404

        project = Project.objects.get(project_uuid=project_id)
        data['project'] = project
        data['initiator'] = request.user


class ScanListView(ListAPIViewBase):
    serializer_class = ScanSerializer
    queryset = Scan.objects.all()

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        return queryset.filter(initiator=self.request.user)


class ScannerView(views.APIView):

    authentication_classes = [
        BasicAuthentication,
        SessionAuthentication,
        TokenAuthentication
    ]

    permission_classes = [IsAuthenticated & IsScanInitiator]

    def get(self, request: Request, scan_id: UUID, name: str,
            extension: str) -> Response:
        """Generates a result JSON for each scanner extension

        :param request: the HttpRequest
        :type request: Request
        :param scan_id: the scan's ID
        :type scan_id: UUID
        :param name: the scanner's name
        :type name: str
        :param extension: the extension to query
        :type extension: str
        :return: the results as JSON string
        :rtype: Response
        """
        # TODO: maybe add pagination
        scan = get_object_or_404(Scan.objects.all(), scan_uuid=scan_id)
        plugins = ScannerPlugin.all_of(scan.project)

        if name not in plugins:
            return Response(status=status.HTTP_404_NOT_FOUND)

        plugin: ScannerPlugin = plugins[name]
        if extension not in plugin.extensions:
            return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

        results = plugin.results(extension, scan)
        return Response(results)


