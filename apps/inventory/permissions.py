from rest_framework.permissions import BasePermission, SAFE_METHODS


class HasInventoryModelPermission(BasePermission):
    permission_map = {}
    app_label = ""
    model_name = ""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated

        if not request.user.is_authenticated:
            return False

        if request.user.role in [request.user.Role.STAFF, request.user.Role.MANAGER]:
            return True

        action = self.permission_map.get(request.method)
        if not action:
            return False

        permission = f"{self.app_label}.{action}_{self.model_name}"
        return request.user.has_perm(permission)


class IsWarehouseManager(HasInventoryModelPermission):
    app_label = "inventory"
    model_name = "warehouse"
    permission_map = {
        "POST": "add",
        "PUT": "change",
        "PATCH": "change",
        "DELETE": "delete",
    }


class IsInventoryManager(HasInventoryModelPermission):
    app_label = "inventory"
    model_name = "inventory"
    permission_map = {
        "POST": "add",
        "PUT": "change",
        "PATCH": "change",
        "DELETE": "delete",
    }
