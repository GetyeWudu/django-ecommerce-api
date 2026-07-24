# apps/products/serializers/__init__.py

from .category import (
    CategorySerializer,
    CategoryReadSerializer,
)

from .tag import (
    TagSerializer,
    TagReadSerializer,
)

from .attributeValue import (
    VariantAttributeValueSerializer,
    AttributeValueSerializer,
    AttributeSerializer,
)

from .variant import (
    ProductVariantReadSerializer,
    ProductVariantWriteSerializer,
)

from .productImage import (
    ProductImageSerializer,
)

from .product import (
    ProductReadSerializer,
    ProductWriteSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
)


__all__ = [
    "CategorySerializer",
    "CategoryReadSerializer",

    "TagSerializer",
    "TagReadSerializer",

    "VariantAttributeValueSerializer",
    "AttributeValueSerializer",
    "AttributeSerializer",

    "ProductVariantReadSerializer",
    "ProductVariantWriteSerializer",

    "ProductImageSerializer",

    "ProductReadSerializer",
    "ProductWriteSerializer",
    "ProductDetailSerializer",
    "ProductListSerializer",
]