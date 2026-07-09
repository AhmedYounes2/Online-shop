from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from cart.forms import CartAddProductForm
from shop.models import Category, Product


class BaseProductViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            name="Tea",
            slug="tea",
        )

        cls.product = Product.objects.create(
            category=cls.category,
            name="Green tea",
            slug="green-tea",
            price=Decimal("29.99"),
            available=True,
        )

        cls.hidden_product = Product.objects.create(
            category=cls.category,
            name="Hidden product",
            slug="hidden-product",
            price=Decimal("99.99"),
            available=False,
        )


class ProductListViewTests(BaseProductViewTest):
    def test_product_list_view(self):
        response = self.client.get(reverse("shop:product_list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "shop/product/list.html")
        self.assertContains(response, "Green tea")
        self.assertNotContains(response, "Hidden product")

    def test_product_list_by_category(self):
        response = self.client.get(
            reverse(
                "shop:product_list_by_category",
                args=[self.category.slug],
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["category"], self.category)

        products = response.context["products"]

        self.assertEqual(products.count(), 1)
        self.assertIn(self.product, products)

    def test_invalid_category_returns_404(self):
        response = self.client.get(
            reverse(
                "shop:product_list_by_category",
                args=["not-exist-category"],
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_product_list_context_has_all_categories(self):
        response = self.client.get(reverse("shop:product_list"))

        self.assertIn(self.category, response.context["categories"])


class ProductDetailViewTests(BaseProductViewTest):
    def test_product_detail_view(self):
        response = self.client.get(
            reverse(
                "shop:product_detail",
                args=[self.product.id, self.product.slug],
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "shop/product/detail.html")
        self.assertEqual(response.context["product"], self.product)

    def test_unavailable_product_returns_404(self):
        response = self.client.get(
            reverse(
                "shop:product_detail",
                args=[self.hidden_product.id, self.hidden_product.slug],
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_wrong_slug_returns_404(self):
        response = self.client.get(
            reverse(
                "shop:product_detail",
                args=[self.product.id, "wrong-slug"],
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_product_detail_has_cart_form(self):
        response = self.client.get(
            reverse("shop:product_detail", args=[self.product.id, self.product.slug])
        )

        self.assertIsInstance(response.context["cart_product_form"], CartAddProductForm)