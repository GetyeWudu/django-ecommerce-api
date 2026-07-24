from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import (
    SAFE_METHODS,
    AllowAny,
    IsAuthenticated,
)
from rest_framework.filters import (
    SearchFilter,
    OrderingFilter,
)
from django_filters.rest_framework import DjangoFilterBackend

from apps.accounts.permissions import IsEmailVerified
from apps.products.pagination import ProductPagination
from apps.products.permissions import IsProductManager, IsProductVariantManager
from apps.products.filters import ProductFilter

# Fixed Model Imports
from apps.products.models.product import (
    Category,
    Tag,
    Product,
)
from apps.products.models.productImage import ProductImage
from apps.products.models.variant import ProductVariant
from apps.products.serializers.variant import ProductVariantWriteSerializer
from apps.products.models.attribute import (
    Attribute,
    AttributeValue,
    VariantAttributeValue,
)

# Fixed Serializer Imports
from apps.products.serializers import (
    CategorySerializer,
    ProductWriteSerializer,
    ProductReadSerializer,
    TagSerializer,
    ProductVariantReadSerializer,
    ProductImageSerializer,
    AttributeSerializer,
    AttributeValueSerializer,
)
from apps.products.serializers.variant import ProductVariantWriteSerializer


class CategoryViewSet(
    ModelViewSet
):

    queryset = Category.objects.all()

    serializer_class = CategorySerializer
    permission_classes = [IsProductManager]


class TagViewSet(
    ModelViewSet
):

    queryset = Tag.objects.all()

    serializer_class = TagSerializer
    permission_classes = [IsProductManager]


class ProductViewSet(
    ModelViewSet
):

    queryset = (
        Product.objects
        .filter(
            is_active=True,
        )
        .prefetch_related(
            "categories",
            "tags",
            'variants',
        )
    )
    pagination_class = (
        ProductPagination
    )

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_class = ProductFilter

    search_fields = [
        "name",
        "description",
        "categories__name",
        "tags__name",
    ]

    ordering_fields = [
        "name",
        "created_at",
        "updated_at",
    ]

    ordering = [
        "-created_at",
    ]

    def get_serializer_class(self):

        if self.action in ["list", "retrieve"]:
            return ProductReadSerializer

        return ProductWriteSerializer

    def get_permissions(self):

        if self.request.method in SAFE_METHODS:
            return [
                AllowAny()
            ]

        return [
            IsAuthenticated(),

            IsProductManager(),
        ]


class ProductVariantViewSet(
    ModelViewSet
):

    queryset = (
        ProductVariant.objects
        .filter(
            is_active=True,
        )
        .select_related(
            "product",
        )
        .prefetch_related(
            "attribute_values__attribute_value__attribute",
        )
    )

    def get_permissions(self):

        if self.request.method in SAFE_METHODS:

            return [
                AllowAny()
            ]

        return [
            IsProductManager(),
        ]

    def get_serializer_class(self):

        if self.action in [
            "create",
            "update",
            "partial_update",
        ]:
            return ProductVariantWriteSerializer

        return ProductVariantReadSerializer

    def destroy(
        self,
        request,
        *args,
        **kwargs,
    ):

        instance = self.get_object()

        instance.soft_delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class ProductImageViewSet(
    ModelViewSet
):

    queryset = (
        ProductImage.objects
        .select_related(
            "product",
            "variant",
        )
    )

    serializer_class = (
        ProductImageSerializer
    )

    permission_classes = [


        IsProductManager,
    ]


class AttributeViewSet(
    ModelViewSet
):

    queryset = (
        Attribute.objects
        .filter(
            is_active=True,
        )
        .prefetch_related(
            "attribute_values",
        )
    )

    serializer_class = (
        AttributeSerializer
    )
    permission_classes = [IsProductManager,]


class AttributeValueViewSet(
    ModelViewSet
):

    queryset = (
        AttributeValue.objects
        .filter(
            is_active=True,
        )
        .select_related(
            "attribute",
        )
    )

    serializer_class = (
        AttributeValueSerializer
    )
    permission_classes = [IsProductManager,]
