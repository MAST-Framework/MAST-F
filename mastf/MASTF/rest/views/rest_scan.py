import os
import logging
import shutil

from uuid import UUID

from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
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

__all__ = [
    "ScanView",
    "ScanCreationView",
    "ScanListView",
    "ScannerView",
    "ScanTaskView",
    "MultipleScanCreationView",
    "ScanTaskListView",
]


class ScanView(APIViewBase):
    permission_classes = [IsAuthenticated & (CanEditScan | ReadOnly)]
    model = Scan
    serializer_class = ScanSerializer
    lookup_field = "scan_uuid"

    def on_delete(self, request: Request, obj: Scan) -> None:
        if not obj.file: # happens on certain error cases
            return

        path = obj.project.dir(obj.file.internal_name, create=False)
        try:
            file_path = obj.file.file_path
            if not os.path.exists(obj.file.file_path):
                file_path = obj.project.directory / obj.file.internal_name
                if not path.exists():
                    messages.warning("Could not remove uploaded file!")
                else:
                    file_path = str(file_path)

            shutil.rmtree(str(path))
            os.remove(file_path)
        except OSError as err:
            messages.error(request, str(err), err.__class__.__name__)


class ScanCreationMixin:
    def apply_defaults(self, request, data: dict) -> None:
        if not data.get("project", None) and not data.get("projects", None):
            raise exceptions.ValidationError("Project must not be null")

        data["initiator"] = request.user
        data["risk_level"] = "None"
        data["status"] = "Scheduled"
        if not data["start_date"]:
            # The date would be set automatically
            data.pop("start_date")

        # remove the delivered scanners
        plugins = ScannerPlugin.all()
        selected = []
        for i in range(len(plugins)):
            # Remove each scanner so that it won't be used to create
            # the Scan object
            name = self.request.POST.get(f"selected_scanners_{i}", None).lower()
            internal_name = ScannerPlugin.to_internal_name(str(name))
            if not name or internal_name not in plugins:
                logger.warning("Invalid scanner name (unknown): %s", internal_name)
                break

            # Even if the scanner is present, we have to add it
            # to the list of scanners to start
            selected.append(internal_name)

        if len(selected) == 0:
            logger.warning("No scanner selected - aborting scan generation")
            raise ValueError("At least one scanner has to be selected")

        # As the QueryDict is mutable, we can store the selected
        # parameters before we're starting each scanner
        setattr(self.request.POST, "_mutable", True)
        self.request.POST["selected_scanners"] = selected

        # the file has to be downloaded before any action shoule be executed
        file_url = data.pop("file_url", None)
        if not file_url:
            uploaded_file = handle_scan_file_upload(
                self.request.FILES["file"], data["project"]
            )
            if not uploaded_file:
                raise ValueError("Could not save uploaded file")

            self.request.POST["File"] = uploaded_file
        else:
            raise NotImplementedError("URL not implemented!")


class ScanCreationView(ScanCreationMixin, CreationAPIViewBase):
    form_class = ScanForm
    model = Scan
    permission_classes = [IsAuthenticated]

    def set_defaults(self, request, data: dict) -> None:
        data.pop("projects")
        self.apply_defaults(request, data)

    def on_create(self, request: Request, instance: Scan) -> None:
        instance.save()
        tasks.schedule_scan(
            instance, request.POST["File"], request.POST["selected_scanners"]
        )


class MultipleScanCreationView(ScanCreationMixin, CreationAPIViewBase):
    form_class = ScanForm
    model = Scan
    permission_classes = [IsAuthenticated]

    def create(self, data: dict) -> object:
        projects = data.pop("projects", None)
        if not projects:
            raise exceptions.ValidationError("Projects must not be null")

        for project in projects:
            data["project"] = project
            self.apply_defaults(self.request, data)
            instance = super().create(data)
            tasks.schedule_scan(
                str(instance.pk),
                str(self.request.POST["File"].pk),
                self.request.POST["selected_scanners"],
            )


class ScanListView(ListAPIViewBase):
    serializer_class = ScanSerializer
    queryset = Scan.objects.all()

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        # TODO: maybe control via GET parameter whether public scans
        # should be returned as well
        return queryset.filter(initiator=self.request.user)


class ScannerView(views.APIView):
    authentication_classes = [
        BasicAuthentication,
        SessionAuthentication,
        TokenAuthentication,
    ]

    permission_classes = [IsAuthenticated & CanEditScan]

    def get(
        self, request: Request, scan_uuid: UUID, name: str, extension: str
    ) -> Response:
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
        scan = get_object_or_404(Scan.objects.all(), scan_uuid=scan_uuid)
        plugins = Scanner.names(scan.project)

        if name not in plugins:
            return Response(status=status.HTTP_404_NOT_FOUND)

        plugin: ScannerPlugin = ScannerPlugin.all()[name]
        if extension not in plugin.extensions:
            return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

        results = plugin.results(extension, scan)
        return Response(results)


class ScanTaskView(APIViewBase):
    permission_classes = [IsAuthenticated & Get]
    model = ScanTask
    lookup_field = "celery_id"

    def get(self, *args, **kwargs) -> Response:
        logger.debug(
            "[%s] Task lookup for id='%s'",
            self.__class__.__name__,
            self.kwargs.get("celery_id", None),
        )
        task: ScanTask = self.get_object()
        if not task.celery_id:
            data = {}
        else:
            result = AsyncResult(task.celery_id)
            data = CeleryAsyncResultSerializer(result).data

        return Response(data)


class ScanTaskListView(GetObjectMixin, ListAPIViewBase):
    queryset = ScanTask.objects.all()
    model = Scan
    serializer_class = ScanTaskSerializer
    permission_classes = [IsAuthenticated & CanEditScan]
    lookup_field = "scan_uuid"

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        return queryset.filter(scan=self.get_object())
