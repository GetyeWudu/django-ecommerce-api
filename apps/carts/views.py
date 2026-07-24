from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.decorators import action

from apps.carts.models import Cart, CartItem
from apps.carts.serializers import (
    CartReadSerializer,
    CartItemReadSerializer,
    CartItemCreateSerializer,
    CartItemUpdateSerializer,
)


class CartViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CartReadSerializer

    def get_queryset(self):
        return Cart.objects.filter(
            user=self.request.user
        ).prefetch_related(
            "items__product_variant__product"
        )

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(
            user=self.request.user
        )
        return (
            self.get_queryset()
            .filter(pk=cart.pk)
            .first()
        )

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            self.get_object()
        )
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["post"],
        url_path="clear",
    )
    def clear(self, request, *args, **kwargs):
        cart = self.get_object()
        cart.items.all().delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class CartItemViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            CartItem.objects.filter(
                cart__user=self.request.user
            )
            .select_related(
                "cart",
                "product_variant",
                "product_variant__product",
            )
            .order_by("id")
        )

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return CartItemReadSerializer
        if self.action == "create":
            return CartItemCreateSerializer
        return CartItemUpdateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        cart, _ = Cart.objects.get_or_create(
            user=self.request.user
        )
        context["cart"] = cart
        return context
