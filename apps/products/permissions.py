from rest_framework.permissions import (
    BasePermission,
    SAFE_METHODS,
)


class HasModelPermission(
    BasePermission
):

    permission_map = {}

    app_label = ""

    model_name = ""

    def has_permission(
        self,
        request,
        view,
    ):

        if request.method in SAFE_METHODS:
            return True

        if not request.user.is_authenticated:
            return False

        action = self.permission_map.get(
            request.method
        )

        if not action:
            return False

        permission = (
            f"{self.app_label}."
            f"{action}_{self.model_name}"
        )

        return request.user.has_perm(
            permission
        )


class IsProductManager(
    HasModelPermission
):

    app_label = "products"

    model_name = "product"

    permission_map = {

        "POST": "add",

        "PUT": "change",

        "PATCH": "change",

        "DELETE": "delete",

    }


class IsProductVariantManager(
    HasModelPermission
):

    app_label = "products"

    model_name = "productvariant"

    permission_map = {

        "POST": "add",

        "PUT": "change",

        "PATCH": "change",

        "DELETE": "delete",

    }
