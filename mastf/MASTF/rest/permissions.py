from rest_framework.request import HttpRequest
from rest_framework.permissions import BasePermission, SAFE_METHODS


class ReadOnly(BasePermission):
    '''Checks whether the request is read-only'''
    
    def has_permission(self, request: HttpRequest, view):
        return request.method in SAFE_METHODS
    
class IsOwnerOrPublic(BasePermission):
    
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or str(obj.visibility).lower() == 'public'


class IsUser(BasePermission):
    
    def has_object_permission(self, request, view, obj):
        return request.user == obj
    
class IsScanInitiator(BasePermission):
    
    def has_object_permission(self, request, view, obj):
        return request.user == obj.initiator
    