from rest_framework.request import HttpRequest
from rest_framework.permissions import BasePermission, SAFE_METHODS

from django.contrib import messages

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

class IsOwnerOrPublic(BasePermission):
    
    def has_object_permission(self, request, view, obj):
        
        
        
        if not (obj.owner == request.user or str(obj.visibility).lower() == 'public'):
            messages.error(self.request, "Insufficient permissions to view project", "UnauthorizedError")
            return False
        
        return True


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
