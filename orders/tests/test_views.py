from decimal import Decimal
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from orders.models import Order, OrderItem
from shop.models import Category, Product


VALID_ORDER_DATA = {
    "first_name": "ahmed",
    "last_name": "younes",
    "email": "ahmed@email.com",
    "address": "living in the air",
    "postal_code": "1234",
    "city": "Tanta",
}


class OrderCreateViewGetTests(TestCase):
    def test_get_renders_create_template(self):
        response = self.client.get(reverse("orders:order_create"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "orders/order/create.html")

    def test_get_context_has_empty_form(self):
        response = self.client.get(reverse("orders:order_create"))

        self.assertFalse(response.context["form"].is_bound)
        self.assertIn("form", response.context)

    def test_get_context_has_cart(self):
        response = self.client.get(reverse("orders:order_create"))

        self.assertIn("cart", response.context)


@patch("orders.views.order_created.delay")
class OrderCreateViewPostSingleItemTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Tea",
            slug="tea"
        )
        self.product = Product.objects.create(
            category=self.category,
            name="Green tea",
            slug="green-tea",
            price=Decimal("10.00"),
            available=True,
        )
        self.client.post(
            reverse("cart:cart_add", args=[self.product.id]),
            {
                "quantity": 2,
                "override": False,
            }
        )

    def test_valid_post_creates_order(self, mock_delay):
        self.client.post(reverse("orders:order_create"), VALID_ORDER_DATA)

        self.assertEqual(Order.objects.count(), 1)

    def test_valid_post_creates_order_item_with_correct_data(self, mock_delay):
        self.client.post(reverse("orders:order_create"), VALID_ORDER_DATA)
        order = Order.objects.first()
        item = order.items.first()

        self.assertEqual(order.items.count(), 1)
        self.assertEqual(item.product, self.product)
        self.assertEqual(item.price, Decimal("10.00"))
        self.assertEqual(item.quantity, 2)

    def test_valid_post_clears_the_cart(self, mock_delay):
        self.client.post(reverse("orders:order_create"), VALID_ORDER_DATA)
        cart = self.client.session.get(settings.CART_SESSION_ID)
        self.assertIsNone(cart)

    def test_invalid_post_does_not_create_order(self, mock_delay):
        data = VALID_ORDER_DATA.copy()
        data["email"] = "not-valid-email"
        response = self.client.post(reverse("orders:order_create"), data)

        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "orders/order/create.html")
        self.assertFalse(response.context["form"].is_valid())

    def test_invalid_post_keeps_cart_items(self, mock_delay):
        data = VALID_ORDER_DATA.copy()
        data["email"] = "not-valid-email"
        response = self.client.post(reverse("orders:order_create"), data)
        cart = self.client.session.get(settings.CART_SESSION_ID)

        self.assertIn(str(self.product.id), cart)


@patch("orders.views.order_created.delay")
class OrderCreateViewPostMultipleItemsTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Tea",
            slug="tea"
        )
        self.product_a = Product.objects.create(
            category=self.category,
            name="Green Tea",
            slug="green-tea",
            price=Decimal("10.00"),
            available=True,
        )
        self.product_b = Product.objects.create(
            category=self.category,
            name="Black tea",
            slug="black-tea",
            price=Decimal("5.00"),
            available=True,
        )
        self.client.post(
            reverse("cart:cart_add", args=[self.product_a.id]),
            {
                "quantity": 1, "override": False
            }
        )
        self.client.post(
            reverse("cart:cart_add", args=[self.product_b.id]),
            {
                "quantity": 1, "override": False
            }
        )

    def test_all_cart_items_should_become_order_items(self, mock_delay):
        self.client.post(reverse("orders:order_create"), VALID_ORDER_DATA)
        order = Order.objects.first()

        self.assertEqual(order.items.count(), 2)