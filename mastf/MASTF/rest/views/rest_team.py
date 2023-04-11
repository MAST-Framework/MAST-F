from django.contrib.auth.models import User
from django.db.models import QuerySet, Q

from rest_framework.views import APIView
from rest_framework import permissions, authentication, status
from rest_framework.response import Response
from rest_framework.request import Request

from mastf.MASTF.rest.permissions import IsTeamOwner, ReadOnly, IsTeamMember
from mastf.MASTF.serializers import TeamSerializer
from mastf.MASTF.forms import TeamForm
from mastf.MASTF.models import Team

from .base import APIViewBase, ListAPIViewBase, CreationAPIViewBase


__all__ = [
    'TeamView', 'TeamListView', 'TeamCreationView'
]

class TeamView(APIViewBase):
    permission_classes = [permissions.IsAuthenticated & (ReadOnly | IsTeamOwner)]
    model = Team
    serializer_class = TeamSerializer
    
class TeamListView(ListAPIViewBase):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated & (ReadOnly | IsTeamOwner | IsTeamMember)]
    
    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        return queryset.filter(Q(owner=self.request.user) | Q(users__pk=self.request.user.pk))

class TeamCreationView(CreationAPIViewBase):
    model = TeamSerializer
    form_class = TeamForm
    permission_classes = [permissions.IsAuthenticated]
    
    def set_defaults(self, request: Request, data: dict) -> None:
        data.pop('pk')
        # TODO: transform user primary keys
        return super().set_defaults(request, data)
    
    
    