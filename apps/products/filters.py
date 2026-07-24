import django_filters

from .models.product import Product


class ProductFilter(
    django_filters.FilterSet
):

    category = django_filters.CharFilter(
        field_name="categories__slug",
        lookup_expr="iexact",
    )

    tag = django_filters.CharFilter(
        field_name="tags__slug",
        lookup_expr="iexact",
    )

    is_active = django_filters.BooleanFilter()

    class Meta:

        model = Product

        fields = [
            "category",
            "tag",
            "is_active",
        ]


class ProductFilter(
    django_filters.FilterSet
):

    category = django_filters.CharFilter(
        field_name="categories__slug",
        lookup_expr="iexact",
    )

    tag = django_filters.CharFilter(
        field_name="tags__slug",
        lookup_expr="iexact",
    )

    min_price = django_filters.NumberFilter(
        field_name="variants__price",
        lookup_expr="gte",
    )

    max_price = django_filters.NumberFilter(
        field_name="variants__price",
        lookup_expr="lte",
    )

    is_active = django_filters.BooleanFilter()

    class Meta:

        model = Product

        fields = [
            "category",
            "tag",
            "min_price",
            "max_price",
            "is_active",
        ]        