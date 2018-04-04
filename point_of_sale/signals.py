from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from django.db.models import Sum, F
from .models import RetailOrder, RetailOrderItem

# its on product signals

