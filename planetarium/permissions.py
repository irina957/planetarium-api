from rest_framework import permissions


class IsAdminOrIfAuthenticatedReadOnly(permissions.BasePermission):
    """The request is authenticated as an admin - read/write, if as a user - read only requests"""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff) or (
            request.user
            and request.user.is_authenticated
            and request.method in permissions.SAFE_METHODS
        )
