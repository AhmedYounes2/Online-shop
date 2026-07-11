from decimal import Decimal

from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase

from cart.cart import Cart
from shop.models import Category, Product


class BaseCartTest(TestCase):
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
            price=Decimal("9.99"),
            available=True
        )
        
        cls.other_product = Product.objects.create(
            category=cls.category,
            name="Black tea",
            slug="black-tea",
            price=Decimal("5.00"),
            available=True,
        )

    def setUp(self):
        request = RequestFactory().get("/")

        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

        self.request = request
        self.cart = Cart(request)


class CartInitTests(BaseCartTest):
    def test_cart_is_empty_on_init(self):
        self.assertEqual(len(self.cart.cart), 0)

    def test_cart_stored_in_session(self):
        self.assertIn(settings.CART_SESSION_ID, self.request.session)

    def test_existing_session_cart_is_reused(self):
        self.cart.add(self.product, quantity=2)
        new_cart = Cart(self.request)

        self.assertEqual(len(new_cart), 2)


class CartAddTests(BaseCartTest):
    def test_add_new_product(self):
        self.cart.add(self.product, quantity=1)
        product_id = str(self.product.id)
        
        self.assertIn(product_id, self.cart.cart)
        self.assertEqual(self.cart.cart[product_id]["quantity"], 1)
        self.assertEqual(self.cart.cart[product_id]["price"], str(self.product.price))

    def test_add_marks_session_modified(self):
        self.request.session.modified = False
        self.cart.add(self.product, quantity=1)

        self.assertTrue(self.request.session.modified)

    def test_add_existing_product_increments_quantity(self):
        self.cart.add(self.product, quantity=1)
        self.cart.add(self.product, quantity=2)
        product_id = str(self.product.id)

        self.assertEqual(self.cart.cart[product_id]["quantity"], 3)

    def test_add_with_override_quantity(self):
        self.cart.add(self.product, quantity=1)
        self.cart.add(self.product, quantity=5, override_quantity=True)
        product_id = str(self.product.id)

        self.assertEqual(self.cart.cart[product_id]["quantity"], 5)

    def test_add_multiple_products(self):
        self.cart.add(self.product, quantity=1)
        self.cart.add(self.other_product, quantity=3)
        
        self.assertEqual(len(self.cart.cart), 2)
        self.assertEqual(len(self.cart), 4)


class CartRemoveTests(BaseCartTest):
    def test_remove_existing_product(self):
        self.cart.add(self.product, quantity=1)
        self.cart.remove(self.product)

        self.assertNotIn(str(self.product.id), self.cart.cart)

    def test_remove_marks_session_modified(self):
        self.cart.add(self.product, quantity=1)
        self.request.session.modified = False
        self.cart.remove(self.product)
        self.assertTrue(self.request.session.modified)

    def test_remove_product_not_in_cart_does_nothing(self):
        self.cart.add(self.product, quantity=1)
        self.cart.remove(self.other_product)

        self.assertEqual(len(self.cart.cart), 1)


class CartIterationTests(BaseCartTest):
    def test_iter_yields_product_instance(self):
        self.cart.add(self.product, quantity=2)
        items = list(self.cart)

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["product"], self.product)

    def test_iter_computes_total_price_per_item(self):
        self.cart.add(self.product, quantity=3)
        items = list(self.cart)

        self.assertEqual(items[0]["price"], self.product.price)
        self.assertEqual(items[0]["total_price"], self.product.price * 3)
    
    def test_iter_price_is_decimal(self):
        self.cart.add(self.product, quantity=1)
        items = list(self.cart)

        self.assertIsInstance(items[0]["price"], Decimal)

    def test_iter_with_multiple_products(self):
        self.cart.add(self.product, quantity=1)
        self.cart.add(self.other_product, quantity=2)
        items = list(self.cart)

        self.assertEqual(len(items), 2)


class CartLenTests(BaseCartTest):
    def test_len_empty_cart(self):
        self.assertEqual(len(self.cart), 0)
    
    def test_len_counts_total_quantity_not_distinct_products(self):
        self.cart.add(self.product, quantity=2)
        self.cart.add(self.other_product, quantity=3)

        self.assertEqual(len(self.cart), 5)


class  CartTotalPriceTests(BaseCartTest):
    def test_total_price_empty_cart(self):
        self.assertEqual(self.cart.get_total_price(), 0)

    def test_total_price_single_product(self):
        self.cart.add(self.product, quantity=2)
        
        self.assertEqual(self.cart.get_total_price(), self.product.price * 2)

    def test_total_price_multiple_products(self):
        self.cart.add(self.product, quantity=2)
        self.cart.add(self.other_product, quantity=1)
        expected = (self.product.price * 2) + (self.other_product.price * 1)

        self.assertEqual(self.cart.get_total_price(), expected)


class CartClearTests(BaseCartTest):
    def test_clear_removes_cart_from_session(self):
        self.cart.add(self.product, quantity=1)
        self.cart.clear()

        self.assertNotIn(settings.CART_SESSION_ID, self.request.session)

    def test_clear_marks_session_modified(self):
        self.cart.add(self.product, quantity=1)
        self.request.session.modified = False
        self.cart.clear()

        self.assertTrue(self.request.session.modified)