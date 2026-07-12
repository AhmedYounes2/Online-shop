from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.conf import settings

from shop.models import Category, Product


class CartAddViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Tea",
            slug="tea",
        )

        self.product = Product.objects.create(
            category=self.category,
            name="Green Tea",
            slug="green-tea",
            price=Decimal("10.00"),
            available=True
        )

    def test_cart_add_adds_product_to_session_cart(self):
        response = self.client.post(
            reverse("cart:cart_add", args=[self.product.id]),
            {
                "quantity": 2,
                "override": False,
            },
        )

        self.assertRedirects(response, reverse("cart:cart_detail"))

        cart = self.client.session[settings.CART_SESSION_ID]

        self.assertIn(str(self.product.id), cart)
        self.assertEqual(cart[str(self.product.id)]["quantity"], 2)
        self.assertEqual(cart[str(self.product.id)]["price"], "10.00")

    
    def test_cart_add_only_accepts_post(self):
        response = self.client.get(
            reverse("cart:cart_add", args=[self.product.id])
        )

        self.assertEqual(response.status_code, 405)


class CartRemoveViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Tea",
            slug="tea",
        )

        self.product = Product.objects.create(
            category=self.category,
            name="Green Tea",
            slug="green-tea",
            price=Decimal("10.00"),
            available=True
        )

    def test_cart_remove_removes_product_from_cart(self):
        self.client.post(
            reverse("cart:cart_add", args=[self.product.id]),
            {
                "quantity": 2,
                "override": False,
            },
        )

        response = self.client.post(
            reverse("cart:cart_remove", args=[self.product.id])
        )

        self.assertRedirects(response, reverse("cart:cart_detail"))

        cart = self.client.session[settings.CART_SESSION_ID]

        self.assertNotIn(str(self.product.id), cart)

    def test_cart_remove_only_accepts_post(self):
        response = self.client.get(
            reverse("cart:cart_remove", args=[self.product.id])
        )

        self.assertEqual(response.status_code, 405)


class CartDetailViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Tea",
            slug="tea",
        )

        self.product = Product.objects.create(
            category=self.category,
            name="Green tea",
            slug="green-tea",
            price=Decimal("10.00"),
            available=True
        )

    def test_cart_detail_display_all_items_in_cart(self):
        self.client.post(
            reverse("cart:cart_add", args=[self.product.id]),
            {
                "quantity": 2,
                "override": False,
            },
        )

        response = self.client.get(reverse("cart:cart_detail"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Green tea")
        self.assertTemplateUsed(response, "cart/detail.html")

    def test_cart_detail_empty_cart(self):
        response = self.client.get(reverse("cart:cart_detail"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["cart"]), 0)

    def test_cart_detail_item_has_update_quantity_form(self):
        self.client.post(
            reverse("cart:cart_add", args=[self.product.id]),
            {
                "quantity": 2,
                "override": False,
            },
        )

        response = self.client.get(reverse("cart:cart_detail"))

        cart = response.context["cart"]
        items = list(cart)

        self.assertEqual(len(items), 1)
        self.assertIn("update_quantity_form", items[0])
        self.assertEqual(items[0]["update_quantity_form"].initial["quantity"], 2)
        self.assertEqual(items[0]["update_quantity_form"].initial["override"], True)
