from rest_framework import serializers

from apps.inventory.models import Inventory, Warehouse


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = [
            "id",
            "name",
            "code",
            "address",
            "city",
            "country",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class InventoryReadSerializer(serializers.ModelSerializer):
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)
    warehouse_code = serializers.CharField(source="warehouse.code", read_only=True)
    variant_sku = serializers.CharField(source="product_variant.sku", read_only=True)
    available_quantity = serializers.IntegerField(read_only=True)

    class Meta:
        model = Inventory
        fields = [
            "id",
            "warehouse",
            "warehouse_name",
            "warehouse_code",
            "product_variant",
            "variant_sku",
            "quantity",
            "reserved_quantity",
            "available_quantity",
            "created_at",
            "updated_at",
        ]


class InventoryWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = [
            "id",
            "warehouse",
            "product_variant",
            "quantity",
            "reserved_quantity",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate(self, attrs):
        quantity = attrs.get("quantity", getattr(self.instance, "quantity", 0))
        reserved_quantity = attrs.get(
            "reserved_quantity", getattr(self.instance, "reserved_quantity", 0)
        )

        if reserved_quantity > quantity:
            raise serializers.ValidationError(
                {"reserved_quantity": "Reserved quantity cannot be greater than quantity."}
            )

        warehouse = attrs.get("warehouse", getattr(self.instance, "warehouse", None))
        product_variant = attrs.get(
            "product_variant", getattr(self.instance, "product_variant", None)
        )

        if warehouse and product_variant:
            duplicate_qs = Inventory.objects.filter(
                warehouse=warehouse,
                product_variant=product_variant,
            )
            if self.instance:
                duplicate_qs = duplicate_qs.exclude(id=self.instance.id)
            if duplicate_qs.exists():
                raise serializers.ValidationError(
                    {
                        "non_field_errors": [
                            "Inventory for this warehouse and variant already exists."
                        ]
                    }
                )

        return attrs


class InventoryQuantitySerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)


class InventoryAdjustSerializer(serializers.Serializer):
    delta = serializers.IntegerField()
