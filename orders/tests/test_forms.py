from django.test import TestCase

from orders.forms import OrderCreateForm

VALID_DATA = {
    "first_name": "ahmed",
    "last_name": "younes",
    "email": "ahmed@email.com",
    "address": "living in the air",
    "postal_code": "1234",
    "city": "Tanta",
}

class OrderCreateFormTests(TestCase):
    def test_valid_data(self):
        form = OrderCreateForm(data=VALID_DATA)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["first_name"], "ahmed")
        self.assertEqual(form.cleaned_data["last_name"], "younes")
        self.assertEqual(form.cleaned_data["email"], "ahmed@email.com")
        self.assertEqual(form.cleaned_data["address"], "living in the air")
        self.assertEqual(form.cleaned_data["postal_code"], "1234")
        self.assertEqual(form.cleaned_data["city"], "Tanta")

    def test_invalid_email(self):
        data = VALID_DATA.copy()
        data["email"] = "not-an-email"
        form = OrderCreateForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_missing_first_name(self):
        data = VALID_DATA.copy()
        del data["first_name"]
        form = OrderCreateForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("first_name", form.errors)
    
    def test_missing_last_name(self):
        data = VALID_DATA.copy()
        del data["last_name"]
        form = OrderCreateForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("last_name", form.errors)

    def test_missing_email(self):
        data = VALID_DATA.copy()
        del data["email"]
        form = OrderCreateForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_missing_address(self):
        data = VALID_DATA.copy()
        del data["address"]
        form = OrderCreateForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("address", form.errors)

    def test_missing_postal_code(self):
        data = VALID_DATA.copy()
        del data["postal_code"]
        form = OrderCreateForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("postal_code", form.errors)

    def test_missing_city(self):
        data = VALID_DATA.copy()
        del data["city"]
        form = OrderCreateForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("city", form.errors)

    def test_empty_form_is_invalid(self):
        form = OrderCreateForm(data={})

        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), len(VALID_DATA))