from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

from apps.products.models.variant import ProductVariant


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart({self.user_id})"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name="cart_items",
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product_variant"],
                name="unique_cart_item_variant",
            ),
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name="cart_item_quantity_gt_0",
            ),
        ]
        indexes = [
            models.Index(fields=["cart", "product_variant"]),
        ]

    def __str__(self):
        return f"CartItem(cart={self.cart_id}, variant={self.product_variant_id})"
