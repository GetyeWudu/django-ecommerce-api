from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import F, Q

from apps.products.models.base import SoftDeleteManager, SoftDeleteModel
from apps.products.models.variant import ProductVariant


class Warehouse(SoftDeleteModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def __str__(self):
        return f"{self.name} ({self.code})"


class Inventory(SoftDeleteModel):
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="inventories",
    )
    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name="inventories",
    )
    quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["warehouse", "product_variant"],
                condition=Q(is_deleted=False),
                name="unique_active_inventory_warehouse_variant",
            ),
            models.CheckConstraint(
                condition=Q(quantity__gte=0),
                name="inventory_quantity_gte_0",
            ),
            models.CheckConstraint(
                condition=Q(reserved_quantity__gte=0),
                name="inventory_reserved_quantity_gte_0",
            ),
            models.CheckConstraint(
                condition=Q(quantity__gte=F("reserved_quantity")),
                name="inventory_reserved_lte_quantity",
            ),
        ]

    def __str__(self):
        return f"{self.product_variant.sku} @ {self.warehouse.code}"

    @property
    def available_quantity(self):
        return self.quantity - self.reserved_quantity

    def clean(self):
        if self.quantity < 0:
            raise ValidationError({"quantity": "Quantity must be greater than or equal to 0."})
        if self.reserved_quantity < 0:
            raise ValidationError(
                {"reserved_quantity": "Reserved quantity must be greater than or equal to 0."}
            )
        if self.reserved_quantity > self.quantity:
            raise ValidationError(
                {"reserved_quantity": "Reserved quantity cannot be greater than quantity."}
            )

    def reserve(self, quantity):
        if quantity <= 0:
            raise ValidationError({"quantity": "Reserve quantity must be greater than 0."})
        if quantity > self.available_quantity:
            raise ValidationError({"quantity": "Insufficient available stock."})

        self.reserved_quantity += quantity
        self.full_clean()
        self.save(update_fields=["reserved_quantity", "updated_at"])

    def release(self, quantity):
        if quantity <= 0:
            raise ValidationError({"quantity": "Release quantity must be greater than 0."})
        if quantity > self.reserved_quantity:
            raise ValidationError(
                {"quantity": "Release quantity cannot be greater than reserved quantity."}
            )

        self.reserved_quantity -= quantity
        self.full_clean()
        self.save(update_fields=["reserved_quantity", "updated_at"])

    def adjust(self, delta):
        new_quantity = self.quantity + delta
        if new_quantity < 0:
            raise ValidationError({"quantity": "Adjustment would result in negative stock."})
        if self.reserved_quantity > new_quantity:
            raise ValidationError(
                {"quantity": "Quantity cannot be lower than reserved quantity."}
            )

        self.quantity = new_quantity
        self.full_clean()
        self.save(update_fields=["quantity", "updated_at"])

    @classmethod
    @transaction.atomic
    def reserve_atomic(cls, inventory_id, quantity):
        inventory = cls.objects.select_for_update().get(id=inventory_id)
        inventory.reserve(quantity)
        return inventory

    @classmethod
    @transaction.atomic
    def release_atomic(cls, inventory_id, quantity):
        inventory = cls.objects.select_for_update().get(id=inventory_id)
        inventory.release(quantity)
        return inventory

    @classmethod
    @transaction.atomic
    def adjust_atomic(cls, inventory_id, delta):
        inventory = cls.objects.select_for_update().get(id=inventory_id)
        inventory.adjust(delta)
        return inventory
