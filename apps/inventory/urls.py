from rest_framework.routers import DefaultRouter

from apps.inventory.views import InventoryViewSet, WarehouseViewSet

router = DefaultRouter()
router.register("warehouses", WarehouseViewSet)
router.register("stock", InventoryViewSet)

urlpatterns = router.urls
