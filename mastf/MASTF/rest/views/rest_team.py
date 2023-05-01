from django.contrib.auth.models import User
from django.db.models import QuerySet, Q

from rest_framework.views import APIView
from rest_framework import permissions, authentication, status
from rest_framework.response import Response
from rest_framework.request import Request

from mastf.MASTF.serializers import TeamSerializer
from mastf.MASTF.forms import TeamForm, EditTeamMembersForm
from mastf.MASTF.models import Team
from mastf.MASTF.permissions import CanEditTeam, CanDeleteTeam, CanViewTeam, Patch

from .base import APIViewBase, ListAPIViewBase, CreationAPIViewBase, GetObjectMixin


__all__ = [
    'TeamView', 'TeamListView', 'TeamCreationView', 'TeamMemberView'
]

class TeamView(APIViewBase):
    permission_classes = [permissions.IsAuthenticated & (CanViewTeam | CanEditTeam | CanDeleteTeam)]
    model = Team
    serializer_class = TeamSerializer
    bound_permissions = [CanEditTeam]

class TeamListView(ListAPIViewBase):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated & CanViewTeam]

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        return queryset.filter(Q(owner=self.request.user) | Q(users__pk=self.request.user.pk))

class TeamCreationView(CreationAPIViewBase):
    model = Team
    form_class = TeamForm
    permission_classes = [permissions.IsAuthenticated]
    bound_permissions = [CanEditTeam, CanDeleteTeam, CanViewTeam]

    def set_defaults(self, request: Request, data: dict) -> None:
        # The primary key will be set automatically by Django
        data.pop("pk")

    def on_create(self, request: Request, instance) -> None:
        for user in instance.users.all():
            if user != self.request.user:
                CanViewTeam.assign_to(user, instance.pk)


class TeamMemberView(GetObjectMixin, APIView):
    authentication_classes = [
        authentication.BasicAuthentication,
        authentication.SessionAuthentication,
        authentication.TokenAuthentication
    ]
    model = Team
    permission_classes = [permissions.IsAuthenticated & (CanEditTeam | Patch)]

    def put(self, request, *args, **kwargs):
        team: Team = self.get_object()

        form = EditTeamMembersForm(data=request.data)
        valid = form.is_valid()
        if valid:
            team.users.add(*form.cleaned_data['users'])

        return Response({'success': valid})

    def patch(self, request, *args, **kwargs):
        team: Team = self.get_object()

        form = EditTeamMembersForm(data=request.data)
        valid = form.is_valid()
        if valid:
            permission = CanEditTeam.get(team)
            for user in form.cleaned_data['users']:
                if user == self.request.user or (permission in self.request.user.user_permissions.all()):
                    team.users.remove(user)
                    CanViewTeam.remove_from(user, team)
                    CanEditTeam.remove_from(user, team)
                    CanDeleteTeam.remove_from(user, team)

        return Response({'success': valid})

