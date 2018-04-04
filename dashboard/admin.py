from django.contrib import admin

# Register your models here.
from .models import *


@admin.register(PaymentOrders)
class PaymentOrdersAdmin(admin.ModelAdmin):
	pass
		


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
	pass
