from django.contrib import admin

from apps.inventory.models import Inventory, Warehouse


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code", "city", "country", "is_active", "is_deleted")
    search_fields = ("name", "code", "city", "country")
    list_filter = ("is_active", "is_deleted", "country")


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "warehouse",
        "product_variant",
        "quantity",
        "reserved_quantity",
        "available_quantity",
        "is_deleted",
    )
    search_fields = ("warehouse__name", "warehouse__code", "product_variant__sku")
    list_filter = ("warehouse", "is_deleted")
