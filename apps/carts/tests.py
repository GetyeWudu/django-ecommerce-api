from unittest.mock import patch

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.carts.models import Cart, CartItem
from apps.products.models.product import Product
from apps.products.models.variant import ProductVariant


User = get_user_model()


class CartAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com",
            "testpass123",
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            "testpass123",
        )
        self.product = Product.objects.create(
            name="Demo Product",
            is_active=True,
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            sku="SKU-1",
            price="100.00",
            currency="ETB",
            is_active=True,
        )
        self.cart_url = "/api/v1/cart/"
        self.cart_items_url = "/api/v1/cart/items/"

    def authenticate(self, user=None):
        self.client.force_authenticate(user=user or self.user)

    def test_auth_required_for_cart_endpoints(self):
        response = self.client.get(self.cart_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        response = self.client.post(
            self.cart_items_url,
            {
                "product_variant": self.variant.id,
                "quantity": 1,
            },
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    @patch(
        "apps.carts.serializers.get_available_stock",
        return_value=10,
    )
    def test_add_item_success(self, _mock_stock):
        self.authenticate()

        response = self.client.post(
            self.cart_items_url,
            {
                "product_variant": self.variant.id,
                "quantity": 2,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(CartItem.objects.count(), 1)
        self.assertEqual(
            CartItem.objects.get().quantity,
            2,
        )

    @patch(
        "apps.carts.serializers.get_available_stock",
        return_value=5,
    )
    def test_duplicate_add_merges_quantity(
        self,
        _mock_stock,
    ):
        self.authenticate()
        self.client.post(
            self.cart_items_url,
            {
                "product_variant": self.variant.id,
                "quantity": 2,
            },
            format="json",
        )

        response = self.client.post(
            self.cart_items_url,
            {
                "product_variant": self.variant.id,
                "quantity": 3,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(CartItem.objects.count(), 1)
        self.assertEqual(
            CartItem.objects.get().quantity,
            5,
        )

    @patch(
        "apps.carts.serializers.get_available_stock",
        return_value=2,
    )
    def test_reject_quantity_above_stock(
        self,
        _mock_stock,
    ):
        self.authenticate()
        response = self.client.post(
            self.cart_items_url,
            {
                "product_variant": self.variant.id,
                "quantity": 3,
            },
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("quantity", response.data)

    def test_reject_quantity_less_or_equal_zero(self):
        self.authenticate()
        response = self.client.post(
            self.cart_items_url,
            {
                "product_variant": self.variant.id,
                "quantity": 0,
            },
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("quantity", response.data)

    @patch(
        "apps.carts.serializers.get_available_stock",
        return_value=10,
    )
    def test_reject_inactive_product(self, _mock_stock):
        self.authenticate()
        self.product.is_active = False
        self.product.save(update_fields=["is_active"])

        response = self.client.post(
            self.cart_items_url,
            {
                "product_variant": self.variant.id,
                "quantity": 1,
            },
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("product_variant", response.data)

    @patch(
        "apps.carts.serializers.get_available_stock",
        return_value=10,
    )
    def test_reject_inactive_variant(self, _mock_stock):
        self.authenticate()
        self.variant.is_active = False
        self.variant.save(update_fields=["is_active"])

        response = self.client.post(
            self.cart_items_url,
            {
                "product_variant": self.variant.id,
                "quantity": 1,
            },
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("product_variant", response.data)

    @patch(
        "apps.carts.serializers.get_available_stock",
        return_value=6,
    )
    def test_user_can_only_access_own_items(
        self,
        _mock_stock,
    ):
        user_cart = Cart.objects.create(user=self.user)
        item = CartItem.objects.create(
            cart=user_cart,
            product_variant=self.variant,
            quantity=2,
        )
        other_cart = Cart.objects.create(user=self.other_user)
        CartItem.objects.create(
            cart=other_cart,
            product_variant=self.variant,
            quantity=1,
        )

        self.authenticate(self.user)
        response = self.client.get(self.cart_items_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], item.id)

        self.authenticate(self.other_user)
        response = self.client.get(
            f"/api/v1/cart/items/{item.id}/"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    @patch(
        "apps.carts.serializers.get_available_stock",
        return_value=5,
    )
    def test_update_quantity_validations(
        self,
        _mock_stock,
    ):
        self.authenticate()
        create_response = self.client.post(
            self.cart_items_url,
            {
                "product_variant": self.variant.id,
                "quantity": 2,
            },
            format="json",
        )
        item_id = create_response.data["id"]

        response = self.client.patch(
            f"/api/v1/cart/items/{item_id}/",
            {"quantity": 4},
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            CartItem.objects.get(id=item_id).quantity,
            4,
        )

        response = self.client.patch(
            f"/api/v1/cart/items/{item_id}/",
            {"quantity": 6},
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("quantity", response.data)

    @patch(
        "apps.carts.serializers.get_available_stock",
        return_value=10,
    )
    def test_remove_item_and_clear_cart(
        self,
        _mock_stock,
    ):
        self.authenticate()
        first = self.client.post(
            self.cart_items_url,
            {
                "product_variant": self.variant.id,
                "quantity": 1,
            },
            format="json",
        ).data["id"]
        other_variant = ProductVariant.objects.create(
            product=self.product,
            sku="SKU-2",
            price="99.00",
            currency="ETB",
            is_active=True,
        )
        self.client.post(
            self.cart_items_url,
            {
                "product_variant": other_variant.id,
                "quantity": 1,
            },
            format="json",
        )

        response = self.client.delete(
            f"/api/v1/cart/items/{first}/"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertEqual(CartItem.objects.count(), 1)

        response = self.client.post(
            "/api/v1/cart/clear/"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertEqual(CartItem.objects.count(), 0)
