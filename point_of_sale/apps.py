from django.apps import AppConfig


class PosConfig(AppConfig):
    name = 'PoS'

    def ready(self):
        import PoS.signals