from django.db import models
from .variant import ProductVariant
from django.core.exceptions import ValidationError
from apps.products.utils import generate_unique_slug

class Attribute(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True,
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    def __str__(self):
        return self.name


class AttributeValue(models.Model):

    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.PROTECT,
        related_name="attribute_values",
    )

    value = models.CharField(
        max_length=100,
    )

    slug = models.SlugField(
        max_length=120,blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "attribute",
                    "value",
                ],
                name=(
                    "unique_attribute_value"
                ),
            ),
        ]

    def __str__(self):
        return (
            f"{self.attribute.name}: "
            f"{self.value}"
        )
class VariantAttributeValue(models.Model):

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name="attribute_values",
    )

    attribute_value = models.ForeignKey(
        AttributeValue,
        on_delete=models.PROTECT,
        related_name="variant_assignments",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "variant",
                    "attribute_value",
                ],
                name="unique_variant_attribute_value",
            ),
        ]

    def __str__(self):

        return (
            f"{self.variant.sku} - "
            f"{self.attribute_value.attribute.name}: "
            f"{self.attribute_value.value}"
        )