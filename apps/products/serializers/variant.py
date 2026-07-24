from django.db import transaction
from rest_framework import serializers

from apps.products.models.variant import ProductVariant
from apps.products.models.attribute import (
    AttributeValue,
    VariantAttributeValue,
)


class ProductVariantReadSerializer(
    serializers.ModelSerializer
):
    """
    Serializer used when reading/retrieving ProductVariants.

    Example response:

    {
        "id": 7,
        "product": 10,
        "sku": "BAGGY-BLU-L",
        "price": "2800.00",
        "currency": "ETB",
        "is_default": false,
        "is_active": true,
        "attribute_values": [
            {
                "attribute": "Color",
                "value": "Blue"
            },
            {
                "attribute": "Size",
                "value": "Large"
            }
        ]
    }
    """

    attribute_values = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant

        fields = [
            "id",
            "product",
            "sku",
            "price",
            "currency",
            "is_default",
            "is_active",
            "attribute_values",
        ]

    def get_attribute_values(self, obj):
        """
        Get AttributeValue objects through the
        VariantAttributeValue intermediate model.
        """

        attribute_values = (
            AttributeValue.objects
            .filter(
                variant_assignments__variant=obj
            )
            .select_related("attribute")
        )

        return [
            {
                "attribute": attribute_value.attribute.name,
                "value": attribute_value.value,
            }
            for attribute_value in attribute_values
        ]


class ProductVariantWriteSerializer(
    serializers.ModelSerializer
):
    """
    Serializer used when creating or updating
    ProductVariants.

    The client sends AttributeValue IDs.

    Example:

    {
        "product": 10,
        "sku": "BAGGY-BLU-L",
        "price": "2800.00",
        "currency": "ETB",
        "is_default": false,
        "is_active": true,
        "attribute_values": [3, 7]
    }
    """

    attribute_values = serializers.PrimaryKeyRelatedField(
        queryset=AttributeValue.objects.all(),
        many=True,
        required=False,
    )

    class Meta:
        model = ProductVariant

        fields = [
            "product",
            "sku",
            "price",
            "currency",
            "is_default",
            "is_active",
            "attribute_values",
        ]

    def validate_attribute_values(
        self,
        attribute_values
    ):
        """
        Prevent assigning multiple values from
        the same Attribute to one ProductVariant.

        Example:

        Color = Red
        Color = Blue

        This should NOT be allowed on the
        same variant.
        """

        attribute_ids = [
            attribute_value.attribute_id
            for attribute_value in attribute_values
        ]

        if len(attribute_ids) != len(
            set(attribute_ids)
        ):
            raise serializers.ValidationError(
                "A product variant can only have "
                "one value for each attribute."
            )

        return attribute_values

    @transaction.atomic
    def create(
        self,
        validated_data
    ):
        attribute_values = validated_data.pop(
            "attribute_values",
            []
        )

        variant = ProductVariant.objects.create(
            **validated_data
        )

        join_instances = [
            VariantAttributeValue(
                variant=variant,
                attribute_value=attribute_value,
            )
            for attribute_value in attribute_values
        ]

        VariantAttributeValue.objects.bulk_create(
            join_instances
        )

        return variant

    @transaction.atomic
    def update(
        self,
        instance,
        validated_data
    ):
        attribute_values = validated_data.pop(
            "attribute_values",
            None
        )

        # Update normal ProductVariant fields
        for attr, value in validated_data.items():
            setattr(
                instance,
                attr,
                value
            )

        instance.save()

        # Only replace attribute values if they
        # were included in the request.
        if attribute_values is not None:

            VariantAttributeValue.objects.filter(
                variant=instance
            ).delete()

            join_instances = [
                VariantAttributeValue(
                    variant=instance,
                    attribute_value=attribute_value,
                )
                for attribute_value in attribute_values
            ]

            VariantAttributeValue.objects.bulk_create(
                join_instances
            )

        return instance
