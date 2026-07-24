from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.inventory.models import Inventory, Warehouse
from apps.products.models.product import Product
from apps.products.models.variant import ProductVariant


class InventoryModelTests(APITestCase):
    def setUp(self):
        self.product = Product.objects.create(name="Sneaker")
        self.variant = ProductVariant.objects.create(
            product=self.product,
            sku="SNKR-BLK-40",
            price="100.00",
            currency="ETB",
        )
        self.warehouse = Warehouse.objects.create(name="Main", code="WH-MAIN")

    def test_available_quantity_property(self):
        inventory = Inventory.objects.create(
            warehouse=self.warehouse,
            product_variant=self.variant,
            quantity=10,
            reserved_quantity=4,
        )

        self.assertEqual(inventory.available_quantity, 6)

    def test_reserve_release_adjust_behavior(self):
        inventory = Inventory.objects.create(
            warehouse=self.warehouse,
            product_variant=self.variant,
            quantity=10,
            reserved_quantity=2,
        )

        Inventory.reserve_atomic(inventory.id, 3)
        inventory.refresh_from_db()
        self.assertEqual(inventory.reserved_quantity, 5)

        Inventory.release_atomic(inventory.id, 2)
        inventory.refresh_from_db()
        self.assertEqual(inventory.reserved_quantity, 3)

        Inventory.adjust_atomic(inventory.id, -2)
        inventory.refresh_from_db()
        self.assertEqual(inventory.quantity, 8)

    def test_prevent_invalid_reservation_and_negative_stock(self):
        inventory = Inventory.objects.create(
            warehouse=self.warehouse,
            product_variant=self.variant,
            quantity=5,
            reserved_quantity=1,
        )

        with self.assertRaises(ValidationError):
            Inventory.reserve_atomic(inventory.id, 10)

        with self.assertRaises(ValidationError):
            Inventory.release_atomic(inventory.id, 5)

        with self.assertRaises(ValidationError):
            Inventory.adjust_atomic(inventory.id, -10)

    def test_duplicate_warehouse_variant_prevented(self):
        Inventory.objects.create(
            warehouse=self.warehouse,
            product_variant=self.variant,
            quantity=1,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Inventory.objects.create(
                    warehouse=self.warehouse,
                    product_variant=self.variant,
                    quantity=2,
                )


class InventoryAPITests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            "customer@example.com",
            "ChangeMe123!",
            role=User.Role.CUSTOMER,
        )
        self.staff = User.objects.create_user(
            "staff@example.com",
            "ChangeMe123!",
            role=User.Role.STAFF,
        )

        self.product = Product.objects.create(name="T-Shirt")
        self.variant = ProductVariant.objects.create(
            product=self.product,
            sku="TSHIRT-WHT-M",
            price="50.00",
            currency="ETB",
        )
        self.warehouse = Warehouse.objects.create(name="Central", code="WH-CENTRAL")
        self.inventory = Inventory.objects.create(
            warehouse=self.warehouse,
            product_variant=self.variant,
            quantity=20,
            reserved_quantity=5,
        )

    def test_anonymous_cannot_list_inventory(self):
        response = self.client.get("/api/v1/inventory/stock/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_can_read_but_cannot_write_inventory(self):
        self.client.force_authenticate(user=self.customer)

        list_response = self.client.get("/api/v1/inventory/stock/")
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)

        create_response = self.client.post(
            "/api/v1/inventory/stock/",
            {
                "warehouse": self.warehouse.id,
                "product_variant": self.variant.id,
                "quantity": 10,
                "reserved_quantity": 1,
            },
            format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create_update_inventory_and_warehouse(self):
        self.client.force_authenticate(user=self.staff)

        warehouse_response = self.client.post(
            "/api/v1/inventory/warehouses/",
            {
                "name": "North",
                "code": "WH-NORTH",
            },
            format="json",
        )
        self.assertEqual(warehouse_response.status_code, status.HTTP_201_CREATED)

        create_response = self.client.post(
            "/api/v1/inventory/stock/",
            {
                "warehouse": warehouse_response.data["id"],
                "product_variant": self.variant.id,
                "quantity": 15,
                "reserved_quantity": 2,
            },
            format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        update_response = self.client.patch(
            f"/api/v1/inventory/stock/{create_response.data['id']}/",
            {"quantity": 17},
            format="json",
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)

    def test_duplicate_inventory_pair_rejected_by_api(self):
        self.client.force_authenticate(user=self.staff)

        response = self.client.post(
            "/api/v1/inventory/stock/",
            {
                "warehouse": self.warehouse.id,
                "product_variant": self.variant.id,
                "quantity": 10,
                "reserved_quantity": 0,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_stock_actions_reserve_release_adjust(self):
        self.client.force_authenticate(user=self.staff)

        reserve_response = self.client.post(
            f"/api/v1/inventory/stock/{self.inventory.id}/reserve/",
            {"quantity": 3},
            format="json",
        )
        self.assertEqual(reserve_response.status_code, status.HTTP_200_OK)

        release_response = self.client.post(
            f"/api/v1/inventory/stock/{self.inventory.id}/release/",
            {"quantity": 2},
            format="json",
        )
        self.assertEqual(release_response.status_code, status.HTTP_200_OK)

        adjust_response = self.client.post(
            f"/api/v1/inventory/stock/{self.inventory.id}/adjust/",
            {"delta": -1},
            format="json",
        )
        self.assertEqual(adjust_response.status_code, status.HTTP_200_OK)
