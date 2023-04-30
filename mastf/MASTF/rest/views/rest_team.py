from django.contrib.auth.models import User
from django.db.models import QuerySet, Q

from rest_framework.views import APIView
from rest_framework import permissions, authentication, status
from rest_framework.response import Response
from rest_framework.request import Request

from mastf.MASTF.rest.permissions import ReadOnly
from mastf.MASTF.serializers import TeamSerializer
from mastf.MASTF.forms import TeamForm
from mastf.MASTF.models import Team
from mastf.MASTF.permissions import CanEditTeam

from .base import APIViewBase, ListAPIViewBase, CreationAPIViewBase


__all__ = [
    'TeamView', 'TeamListView', 'TeamCreationView'
]

class TeamView(APIViewBase):
    permission_classes = [permissions.IsAuthenticated & (ReadOnly | CanEditTeam)]
    model = Team
    serializer_class = TeamSerializer
    bound_permissions = [CanEditTeam]

class TeamListView(ListAPIViewBase):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated & (ReadOnly | CanEditTeam)]

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        return queryset.filter(Q(owner=self.request.user) | Q(users__pk=self.request.user.pk))

class TeamCreationView(CreationAPIViewBase):
    model = TeamSerializer
    form_class = TeamForm
    permission_classes = [permissions.IsAuthenticated]
    bound_permissions = [CanEditTeam]

    def on_create(self, request: Request, instance: Team) -> None:
        CanEditTeam.assign_to(request.user, instance.pk)


