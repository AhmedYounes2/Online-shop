from django.test import TestCase

from cart.forms import CartAddProductForm


class CartAddProductFormTests(TestCase):
    def test_valid_data(self):
        form = CartAddProductForm(data={
            "quantity": 3,
            "override": False
        })

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["quantity"], 3)
        self.assertEqual(form.cleaned_data["override"], False)

    def test_quantity_is_coerced_to_int(self):
        form = CartAddProductForm(data={
            "quantity": 3,
            "override": False,
        })

        self.assertTrue(form.is_valid())
        self.assertIsInstance(form.cleaned_data["quantity"], int)

    def test_quantity_is_required(self):
        form = CartAddProductForm(data={
            "override": False
        })

        self.assertFalse(form.is_valid())
        self.assertIn("quantity", form.errors)

    def test_quantity_out_of_range_is_invalid(self):
        form = CartAddProductForm(data={
            "quantity": 21,
            "override": False
        })

        self.assertFalse(form.is_valid())
        self.assertIn("quantity", form.errors)

    def test_quantity_zero_is_invalid(self):
        form = CartAddProductForm(data={
            "quantity": 0,
            "override": False,
        })

        self.assertFalse(form.is_valid())
        self.assertIn("quantity", form.errors)

    def test_override_default_to_false_when_omitted(self):
        form = CartAddProductForm(data={
            "quantity": 2,
        })

        self.assertTrue(form.is_valid())
        self.assertIs(form.cleaned_data["override"], False)

    def test_override_true(self):
        form = CartAddProductForm(data={
            "quantity": 2,
            "override": True
        })

        self.assertTrue(form.is_valid())
        self.assertIs(form.cleaned_data["override"], True)