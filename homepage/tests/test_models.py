from django.test import TestCase
from products.models import Product



class ProductTest(TestCase):

    def create_whateever(self, title, price):
        return Product.objects.create(title=title,
                                      price=price,
                                      )

    def test_create_whateever(self, title, price):
        w = self.create_whateever(title, price)
        self.assertTrue(isinstance(w, Product))
        self.assertEqual(w.__str__(), w.title)