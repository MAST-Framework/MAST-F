import logging

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

from celery.result import AsyncResult

from mastf.MASTF.serializers import ScanSerializer, CeleryResultSerializer
from mastf.MASTF.models import (
    Scan, 
    Project, 
    ScanTask, 
    ProjectScanner
)
from mastf.MASTF.forms import ScanForm
from mastf.MASTF.rest.permissions import ReadOnly, IsScanInitiator
from mastf.MASTF.scanners.plugin import ScannerPlugin
from mastf.MASTF.utils.upload import handle_scan_file_upload

from .base import (
    APIViewBase, 
    ListAPIViewBase, 
    CreationAPIViewBase, 
    GetObjectMixin
)

logger = logging.getLogger(__name__)

__all__ = [
    'ScanView', 'ScanCreationView', 'ScanListView',
    'ScannerView', 'ScanTaskView'
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
        project_id = data.pop('project_uuid', None)
        if not project_id:
            raise ValueError('Could not find a valid project UUID')

        project = Project.objects.get(project_uuid=project_id)
        data['project'] = project
        data['initiator'] = request.user
        data['risk_level'] = 'None'
        data['status'] = 'Pending'
        
        # remove the delivered scanners
        plugins = ScannerPlugin.all_of(project)
        selected = []
        for i in range(len(plugins)):
            # Remove each scanner so that it won't be used
            # to create the Scan object
            name = data.pop(f"selected_scanners_{i}", None)
            if not name or name not in plugins:
                break
            
            if not ProjectScanner.objects.filter(project=project, scanner=name).exists():
                ProjectScanner(project=project, scanner=name).save()
            # Even if the scanner is present, we have to add it
            # to the list of scanners to start
            selected.append(selected)
        
        if len(selected) == 0:
            logger.warning('No scanner selected - aborting scan generation')
            raise ValueError('At least one scanner has to be selected')
        
        # As the QueryDict is mutable, we can store the selected
        # parameters before we're starting each scanner
        self.request.POST['selected_scanners'] = selected
        # the file has to be downloaded before any action shoule be executed
        if not data.get('file_url', None):
            file = handle_scan_file_upload(self.request.FILES['file'], project)
            if not file:
                raise ValueError('Could not save uploaded file')
            
            data['file'] = file
        
        else:
            raise NotImplementedError('URL not implemented!')
        
        
            
    def on_create(self, request: Request, instance: Scan) -> None:
        # Create desired project scanners
        raise NotImplemented()

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


class ScanTaskView(GetObjectMixin, views.APIView):
    authentication_classes = [
        BasicAuthentication,
        SessionAuthentication,
        TokenAuthentication
    ]

    permission_classes = [IsAuthenticated & IsScanInitiator]

    model = ScanTask
    lookup_field = 'task_uuid'

    def get(self, request: Request, task_uuid: UUID) -> Response:
        task = self.get_object()
        result = AsyncResult(task.celery_id)
        data = CeleryResultSerializer(result).data
        
        return Response(data)
