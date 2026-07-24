from rest_framework import serializers

from apps.carts.models import Cart, CartItem
from apps.carts.stock import get_available_stock
from apps.products.models.variant import ProductVariant


class CartVariantSummarySerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(
        source="product.id",
        read_only=True,
    )
    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
    )

    class Meta:
        model = ProductVariant
        fields = [
            "id",
            "product_id",
            "product_name",
            "sku",
            "price",
            "currency",
            "is_active",
        ]


class CartItemReadSerializer(serializers.ModelSerializer):
    product_variant = CartVariantSummarySerializer(
        read_only=True
    )

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product_variant",
            "quantity",
            "created_at",
            "updated_at",
        ]


class CartReadSerializer(serializers.ModelSerializer):
    items = CartItemReadSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Cart
        fields = [
            "id",
            "items",
            "created_at",
            "updated_at",
        ]


class CartItemCreateSerializer(serializers.ModelSerializer):
    product_variant = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariant.objects.select_related(
            "product"
        )
    )

    class Meta:
        model = CartItem
        fields = ["id", "product_variant", "quantity"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        cart = self.context["cart"]
        product_variant = attrs["product_variant"]
        requested_quantity = attrs["quantity"]

        if not product_variant.is_active:
            raise serializers.ValidationError(
                {
                    "product_variant": (
                        "Inactive product variants "
                        "cannot be added to cart."
                    )
                }
            )

        if not product_variant.product.is_active:
            raise serializers.ValidationError(
                {
                    "product_variant": (
                        "Cannot add variants for "
                        "inactive products."
                    )
                }
            )

        existing_item = CartItem.objects.filter(
            cart=cart,
            product_variant=product_variant,
        ).first()
        target_quantity = requested_quantity
        if existing_item:
            target_quantity += existing_item.quantity

        available_stock = get_available_stock(
            product_variant
        )
        if (
            available_stock is not None
            and target_quantity > available_stock
        ):
            raise serializers.ValidationError(
                {
                    "quantity": (
                        "Requested quantity exceeds "
                        "available stock."
                    )
                }
            )

        return attrs

    def create(self, validated_data):
        cart = self.context["cart"]
        product_variant = validated_data["product_variant"]
        quantity = validated_data["quantity"]

        cart_item = CartItem.objects.filter(
            cart=cart,
            product_variant=product_variant,
        ).first()

        if cart_item:
            cart_item.quantity += quantity
            cart_item.save(update_fields=["quantity", "updated_at"])
            return cart_item

        return CartItem.objects.create(
            cart=cart,
            **validated_data,
        )


class CartItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["id", "quantity"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        quantity = attrs["quantity"]
        product_variant = self.instance.product_variant

        if not product_variant.is_active:
            raise serializers.ValidationError(
                {
                    "product_variant": (
                        "Inactive product variants "
                        "cannot be updated in cart."
                    )
                }
            )

        if not product_variant.product.is_active:
            raise serializers.ValidationError(
                {
                    "product_variant": (
                        "Cannot update variants for "
                        "inactive products."
                    )
                }
            )

        available_stock = get_available_stock(
            product_variant
        )
        if (
            available_stock is not None
            and quantity > available_stock
        ):
            raise serializers.ValidationError(
                {
                    "quantity": (
                        "Requested quantity exceeds "
                        "available stock."
                    )
                }
            )

        return attrs
