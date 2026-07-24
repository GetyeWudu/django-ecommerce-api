from rest_framework.test import (
    APITestCase,
)

class ProductAPITest(
    APITestCase
):

    def test_list_products(
        self,
    ):

        response = self.client.get(
            "/api/v1/catalog/products/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )
def test_anonymous_can_view_products(
    self,
):

    response = self.client.get(
        "/api/v1/catalog/products/"
    )

    self.assertEqual(
        response.status_code,
        200,
    )

def test_customer_cannot_create_product(
    self,
):

    self.client.force_authenticate(
        user=self.customer
    )

    response = self.client.post(
        "/api/v1/catalog/products/",
        {
            "name": "Test Product",
            "slug": "test-product",
            "categories": [
                self.category.id
            ],
        },
        format="json",
    )

    self.assertEqual(
        response.status_code,
        403,
    )

def test_product_manager_can_create_product(
    self,
):

    self.client.force_authenticate(
        user=self.product_manager
    )

    response = self.client.post(
        "/api/v1/catalog/products/",
        {
            "name": "Test Product",
            "slug": "test-product",
            "categories": [
                self.category.id
            ],
        },
        format="json",
    )

    self.assertEqual(
        response.status_code,
        201,
    )


class ProductAPITest(APITestCase):

    def test_list_products(self):

        response = self.client.get(
            "/api/v1/catalog/products/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )


def test_customer_cannot_create_product(self):

    self.client.force_authenticate(
        user=self.customer
    )

    response = self.client.post(
        "/api/v1/catalog/products/",
        {
            "name": "Test Product",
            "slug": "test-product",
            "description": "Test description",
            "categories": [
                self.category.id
            ],
        },
        format="json",
    )

    self.assertEqual(
        response.status_code,
        403,
    )        