from rest_framework.request import HttpRequest
from rest_framework.permissions import (
    BasePermission,
    SAFE_METHODS,
    exceptions
)

from mastf.MASTF.utils.enum import Visibility

class ReadOnly(BasePermission):
    '''Checks whether the request is read-only'''
    def has_permission(self, request: HttpRequest, view):
        return request.method in SAFE_METHODS

class IsUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj


class IsProjectOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

class IsProjectPublic(BasePermission):
    def has_object_permission(self, request, view, obj):
        return not obj.team and obj.visibility == Visibility.PUBLIC

class IsProjectMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user in obj.team.users

CanEditProject = (IsProjectOwner | IsProjectMember | IsProjectPublic)


class IsScanInitiator(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.initiator

class IsScanProjectMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        return CanEditProject().has_object_permission(request, view, obj.project)

CanEditScan = (IsScanInitiator | IsScanProjectMember)

class IsScanTaskInitiator(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.scan.initiator

class IsScanTaskMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        return CanEditProject().has_object_permission(request, view, obj.project)

CanEditScanTask = (IsScanTaskInitiator | IsScanTaskMember)

class IsTeamOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

class IsTeamMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user in obj.users

class CanEditScanAsField(BasePermission):
    ref = CanEditScan()

    def has_object_permission(self, request, view, obj):
        return self.ref.has_object_permission(request, view, obj.scan)

class CanEditScanFromScanner(BasePermission):
    ref = CanEditScanAsField()

    def has_object_permission(self, request, view, obj):
        return self.ref.has_object_permission(request, view, obj.scanner)

class IsBundleMember(BasePermission):
    ref = CanEditProject()

    def has_object_permission(self, request, view, obj):
        for project in obj.projects:
            if not self.ref.has_object_permission(request, view, project):
                return False

        return True
