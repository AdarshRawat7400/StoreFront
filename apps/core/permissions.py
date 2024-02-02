from rest_framework import permissions

SAFE_METHODS = ("GET", "HEAD", "OPTIONS")


class BasePermission(permissions.BasePermission):
    """
    Defining permission methods
    """

    @staticmethod
    def is_customer(request):
        return request.user.is_authenticated and request.user.role == "customer"

    @staticmethod
    def is_admin(request):
        return request.user.is_authenticated and request.user.role == "admin"


    @staticmethod
    def is_superadmin(request):
        return request.user.is_authenticated and request.user.role == "superadmin"


class IsAdmin(BasePermission):
    """
    Checking if user has permission of admin
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "admin" and not request.user.is_deleted


class IsCustomer(BasePermission):
    """
    Checking if user has permission of player
    """

    def has_permission(self, request, view):
        return view.request.user.is_authenticated and request.user.role == "customer" and not request.user.is_deleted


class IsSuperAdmin(BasePermission):
    """
    Checking if user has permission of super admin
    """

    def has_permission(self, request, view):
        return (
            view.request.user.is_authenticated and request.user.role == "superadmin" and not request.user.is_deleted
        )
