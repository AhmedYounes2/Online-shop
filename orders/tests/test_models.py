from decimal import Decimal

from django.test import TestCase

from orders.models import Order, OrderItem
from shop.models import Category, Product


class OrderModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.order = Order.objects.create(
            first_name="Ahmed",
            last_name="Younes",
            email="ahmed@email.com",
            address="123 Main St",
            postal_code="1234",
            city="Tanta",
        )

    def test_order_str(self):
        self.assertEqual(str(self.order), f"Order {self.order.id}")

    def test_order_paid_defaults_to_false(self):
        self.assertFalse(self.order.paid)

    def test_order_created_at_is_set(self):
        self.assertIsNotNone(self.order.created_at)

    def test_order_updated_at_is_set(self):
        self.assertIsNotNone(self.order.updated_at)

    def test_order_ordering(self):
        self.assertEqual(Order._meta.ordering, ["-created_at"])

    def test_get_total_cost_with_no_items(self):
        self.assertEqual(self.order.get_total_cost(), 0)

    def test_get_total_cost_with_items(self):
        category = Category.objects.create(name="Tea", slug="tea")
        product_a = Product.objects.create(
            category=category,
            name="Green Tea",
            slug="green-tea",
            price=Decimal("10.00"),
            available=True,
        )
        product_b = Product.objects.create(
            category=category,
            name="Black Tea",
            slug="black-tea",
            price=Decimal("5.00"),
            available=True,
        )
        OrderItem.objects.create(
            order=self.order,
            product=product_a,
            price=Decimal("10.00"),
            quantity=2
        )
        OrderItem.objects.create(
            order=self.order,
            product=product_b,
            price=Decimal("5.00"),
            quantity=3
        )

        self.assertEqual(self.order.get_total_cost(), Decimal("35.00"))