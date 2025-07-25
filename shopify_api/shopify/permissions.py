from rest_framework import permissions
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied

class CanReadProducts(BasePermission):
    
    def has_permission(self, request, view):
        
        if not request.user.is_authenticated:
            raise PermissionDenied({"success" : False, "message" : "User not authenticated"})
        
        if request.user.groups.filter(name='Product Read').exists():
            return True
        
        raise PermissionDenied({"success" : False, "message" : "User not authorzied to access product details"})
    
class CanEditProducts(BasePermission):
    
    def has_permission(self, request, view):
        
        if not request.user.is_authenticated:
            raise PermissionDenied({"success" : False, "message" : "User not authenticated"})
        
        if request.user.groups.filter(name='Product Edit').exists():
            return True
        
        return PermissionDenied({"success" : False, "message" : "User not authorzied to edit product details"})