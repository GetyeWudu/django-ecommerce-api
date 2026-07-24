from django.apps import apps as django_apps
from django.db.models import F, IntegerField, Sum


def get_available_stock(product_variant):
    try:
        inventory_model = django_apps.get_model(
            "inventory",
            "Inventory",
        )
    except LookupError:
        return None

    queryset = inventory_model.objects.filter(
        product_variant=product_variant
    )

    if not queryset.exists():
        return 0

    field_names = {
        field.name
        for field in inventory_model._meta.fields
    }

    if "available_quantity" in field_names:
        aggregated = queryset.aggregate(
            total=Sum("available_quantity")
        )
        return aggregated["total"] or 0

    if {"quantity", "reserved_quantity"}.issubset(field_names):
        aggregated = queryset.aggregate(
            total=Sum(
                F("quantity") - F("reserved_quantity"),
                output_field=IntegerField(),
            )
        )
        return aggregated["total"] or 0

    if "quantity" in field_names:
        aggregated = queryset.aggregate(
            total=Sum("quantity")
        )
        return aggregated["total"] or 0

    return 0
