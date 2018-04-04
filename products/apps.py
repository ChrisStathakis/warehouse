from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ProductsConfig(AppConfig):
    name = 'products'

    def ready(self):
        import products.signals
        import inventory_manager.signals
        

