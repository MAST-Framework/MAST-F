from uuid import uuid4
from shutil import rmtree

from django.db.models import Q, QuerySet

from rest_framework import permissions
from rest_framework.request import Request

from mastf.MASTF import settings
from mastf.MASTF.rest.permissions import IsOwnerOrPublic
from mastf.MASTF.serializers import ProjectSerializer
from mastf.MASTF.models import Project
from mastf.MASTF.forms import ProjectCreationForm

from .base import ListAPIViewBase, APIViewBase, CreationAPIViewBase

__all__ = [
    'ProjectView', 'ProjectCreationView', 'ProjectListView'
]

class ProjectView(APIViewBase):
    """API-Endpoint designed to create, manage and delete projects.

    The different HTTP methods are mapped as follows:

        - ``GET``: Lists information about a single project
        - ``DELETE``: obviously deletes the current project
        - ``PATCH``: updates single attributes of a project
    """

    permission_classes = [
        # The user has to be authenticated
        permissions.IsAuthenticated & IsOwnerOrPublic
    ]

    model = Project
    serializer_class = ProjectSerializer
    lookup_field = 'project_uuid'

    def on_delete(self, request: Request, obj) -> None:
        rmtree(settings.PROJECTS_ROOT / str(obj.project_uuid))


class ProjectCreationView(CreationAPIViewBase):
    """Basic API-Endpoint to create a new project."""

    permission_classes = [permissions.IsAuthenticated]

    form_class = ProjectCreationForm
    model = Project
    
    def on_create(self, request: Request, instance: Project) -> None:
        path = settings.PROJECTS_ROOT / str(instance.project_uuid)
        path.mkdir()
        
    def set_defaults(self, request: Request, data: dict) -> None:
        data['owner'] = request.user


class ProjectListView(ListAPIViewBase):
    """Lists all projects that can be viewed by a user"""

    queryset = Project.objects.all()
    """Dummy queryset"""

    serializer_class = ProjectSerializer
    # The user must be the owner or the project must be public
    permission_classes = [
        permissions.IsAuthenticated & IsOwnerOrPublic
    ]

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        return queryset.filter(
            Q(owner=self.request.user) | Q(visibility='public')
        )
