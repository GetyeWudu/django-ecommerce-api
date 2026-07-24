from rest_framework import serializers
from apps.products.models import Attribute, AttributeValue
from apps.products.models.attribute import VariantAttributeValue

class VariantAttributeValueSerializer(
    serializers.ModelSerializer
):

    attribute = serializers.CharField(
        source="attribute_value.attribute.name",
        read_only=True,
    )

    value = serializers.CharField(
        source="attribute_value.value",
        read_only=True,
    )

    class Meta:
        model = VariantAttributeValue

        fields = [
            "attribute",
            "value",
        ]

class AttributeValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeValue
        fields = ["id", "attribute", "value", "is_active"]
        read_only_fields = ["id"]


class AttributeSerializer(serializers.ModelSerializer):
    values = AttributeValueSerializer(
        source="attribute_values", many=True, read_only=True
    )

    class Meta:
        model = Attribute
        fields = ["id", "name", "slug", "is_active", "values"]
        read_only_fields = ["id"]