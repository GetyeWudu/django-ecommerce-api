from django.contrib import admin

from .models import (
    Category,
    Tag,
    Attribute,
    AttributeValue,
    Product,
    ProductVariant,
    VariantAttributeValue,
    ProductImage,
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        "name",
        "parent",
        "is_active",
    )

    search_fields = (
        "name",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        "name",
        "is_active",
    )

    search_fields = (
        "name",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "is_active",
        "is_deleted",
        "created_at",
    )

    search_fields = (
        "name",
        "slug",
    )

    list_filter = (
        "is_active",
        "is_deleted",
        "categories",
        "tags",
    )

    filter_horizontal = (
        "categories",
        "tags",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):

    list_display = (
        "sku",
        "product",
        "price",
        "currency",
        "is_default",
        "is_active",
        "is_deleted",
    )

    search_fields = (
        "sku",
        "product__name",
    )

    list_filter = (
        "is_active",
        "is_deleted",
        "is_default",
        "currency",
    )


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "slug",
        "is_active",
    )

    search_fields = (
        "name",
    )


@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):

    list_display = (
        "attribute",
        "value",
        "is_active",
    )

    list_filter = (
        "attribute",
        "is_active",
    )

    search_fields = (
        "value",
        "attribute__name",
    )


@admin.register(VariantAttributeValue)
class VariantAttributeValueAdmin(
    admin.ModelAdmin
):

    list_display = [
        "variant",
        "get_attribute",
        "attribute_value",
    ]

    list_filter = [
        "attribute_value__attribute",
    ]

    search_fields = [
        "variant__sku",
        "attribute_value__value",
        "attribute_value__attribute__name",
    ]

    @admin.display(
        description="Attribute"
    )
    def get_attribute(
        self,
        obj,
    ):
        return obj.attribute_value.attribute.name

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):

    list_display = (
        "product",
        "variant",
        "is_primary",
        "display_order",
    )

    list_filter = (
        "is_primary",
    )                          