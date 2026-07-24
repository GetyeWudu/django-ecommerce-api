from django.urls import path

from apps.carts.views import CartViewSet, CartItemViewSet


cart_view = CartViewSet.as_view(
    {"get": "list"}
)

cart_clear_view = CartViewSet.as_view(
    {"post": "clear"}
)

cart_item_list_view = CartItemViewSet.as_view(
    {
        "get": "list",
        "post": "create",
    }
)

cart_item_detail_view = CartItemViewSet.as_view(
    {
        "get": "retrieve",
        "patch": "partial_update",
        "put": "update",
        "delete": "destroy",
    }
)

urlpatterns = [
    path("", cart_view, name="cart"),
    path("clear/", cart_clear_view, name="cart-clear"),
    path("items/", cart_item_list_view, name="cart-item-list"),
    path(
        "items/<int:pk>/",
        cart_item_detail_view,
        name="cart-item-detail",
    ),
]
