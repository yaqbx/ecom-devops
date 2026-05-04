from rest_framework import permissions


class IsAdminOrSelf(permissions.BasePermission):
    """
    Allow access only to admin users or the user themselves
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or request.user == obj


class IsCompanyAdmin(permissions.BasePermission):
    """
    Allow access to company admins or platform admins
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if hasattr(obj, 'company'):
            return obj.company == request.user.company and request.user.is_company_admin
        return False
    
    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        return request.user.is_company_admin


class IsCompanyMember(permissions.BasePermission):
    """
    Allow access to members of the same company
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if hasattr(obj, 'company'):
            return obj.company == request.user.company
        return False
