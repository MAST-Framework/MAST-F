from rest_framework.request import HttpRequest
from rest_framework.permissions import BasePermission, SAFE_METHODS

from django.contrib import messages

class ReadOnly(BasePermission):
    '''Checks whether the request is read-only'''
    
    def has_permission(self, request: HttpRequest, view):
        return request.method in SAFE_METHODS
    
class IsOwnerOrPublic(BasePermission):
    
    def has_object_permission(self, request, view, obj):
        if not (obj.owner == request.user or str(obj.visibility).lower() == 'public'):
            messages.error(self.request, "Insufficient permissions to view project", "UnauthorizedError")
            return False
        
        return True


class IsUser(BasePermission):
    
    def has_object_permission(self, request, view, obj):
        return request.user == obj
    
class IsScanInitiator(BasePermission):
    
    def has_object_permission(self, request, view, obj):
        return request.user == obj.initiator
    
class IsScanTaskInitiator(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.scan.initiator