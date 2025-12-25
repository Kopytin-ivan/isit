from rest_framework.permissions import BasePermission, SAFE_METHODS


class OrderAccessPermission(BasePermission):
    """
    READ: role.can_view_orders or role.is_admin
    WRITE: role.can_edit_orders or role.is_admin
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        role = getattr(user, "role", None)
        if role is None:
            return False

        if request.method in SAFE_METHODS:
            return bool(role.is_admin or role.can_view_orders)

        return bool(role.is_admin or role.can_edit_orders)

from rest_framework.permissions import BasePermission, SAFE_METHODS

class ReportAccessPermission(BasePermission):
    """
    SAFE (GET/HEAD/OPTIONS): role.can_view_reports or role.is_admin
    WRITE (POST/PATCH/DELETE + generate): role.can_view_reports or role.is_admin
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        role = getattr(user, "role", None)
        if role is None:
            return False

        if request.method in SAFE_METHODS:
            return bool(role.is_admin or role.can_view_reports)

        return bool(role.is_admin or role.can_view_reports)
