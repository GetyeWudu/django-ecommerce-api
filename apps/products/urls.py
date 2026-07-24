from rest_framework.routers import (
    DefaultRouter,
)

from .views import (
    AttributeValueViewSet,
    AttributeViewSet,
    CategoryViewSet,
    TagViewSet,
    ProductViewSet,
    ProductVariantViewSet, 
)

router = DefaultRouter()

router.register(
    "categories",
    CategoryViewSet,
)

router.register(
    "tags",
    TagViewSet,
)

router.register(
    "products",
    ProductViewSet,
)

router.register(
    "variants",
    ProductVariantViewSet,
)

router.register(
    "attributes",
    AttributeViewSet,
)

router.register(
    "attribute-values",
    AttributeValueViewSet,
)

urlpatterns = router.urls