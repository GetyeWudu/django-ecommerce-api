from django.db.models import Prefetch
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.inventory.models import Inventory, Warehouse
from apps.inventory.permissions import IsInventoryManager, IsWarehouseManager
from apps.inventory.serializers import (
    InventoryAdjustSerializer,
    InventoryQuantitySerializer,
    InventoryReadSerializer,
    InventoryWriteSerializer,
    WarehouseSerializer,
)


class WarehouseViewSet(ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsWarehouseManager]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class InventoryViewSet(ModelViewSet):
    queryset = (
        Inventory.objects.select_related(
            "warehouse",
            "product_variant",
            "product_variant__product",
        )
        .prefetch_related(Prefetch("product_variant__attribute_values"))
        .all()
    )

    permission_classes = [IsInventoryManager]

    def get_serializer_class(self):
        if self.action in ["reserve", "release"]:
            return InventoryQuantitySerializer
        if self.action == "adjust":
            return InventoryAdjustSerializer
        if self.action in ["list", "retrieve"]:
            return InventoryReadSerializer
        return InventoryWriteSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], serializer_class=InventoryQuantitySerializer)
    def reserve(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        inventory = Inventory.reserve_atomic(
            inventory_id=self.get_object().id,
            quantity=serializer.validated_data["quantity"],
        )

        return Response(InventoryReadSerializer(inventory).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], serializer_class=InventoryQuantitySerializer)
    def release(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        inventory = Inventory.release_atomic(
            inventory_id=self.get_object().id,
            quantity=serializer.validated_data["quantity"],
        )

        return Response(InventoryReadSerializer(inventory).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], serializer_class=InventoryAdjustSerializer)
    def adjust(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        inventory = Inventory.adjust_atomic(
            inventory_id=self.get_object().id,
            delta=serializer.validated_data["delta"],
        )

        return Response(InventoryReadSerializer(inventory).data, status=status.HTTP_200_OK)
