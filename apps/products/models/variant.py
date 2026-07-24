from django.db import models
from .base import SoftDeleteManager
from .product import Product
from .base import SoftDeleteModel

class ProductVariant(
    SoftDeleteModel
):

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="variants",
    )

    sku = models.CharField(
        max_length=100,
        unique=True,
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    currency = models.CharField(
        max_length=3,
        default="ETB",
    )

    is_default = models.BooleanField(
        default=False,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    objects = SoftDeleteManager()

    all_objects = models.Manager()

    def __str__(self):

        return self.sku
    class Meta:
    
      constraints = [

          models.UniqueConstraint(
              fields=[
                  "product",
              ],
              condition=models.Q(
                  is_default=True,
                  is_deleted=False,
              ),
              name=(
                  "one_active_default_variant"
              ),
          ),
      ]

