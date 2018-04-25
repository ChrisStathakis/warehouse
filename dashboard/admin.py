from django.contrib import admin

# Register your models here.
from .models import *


@admin.register(PaymentOrders)
class PaymentOrdersAdmin(admin.ModelAdmin):
	list_display = ['title', 'date_expired', 'content_type', 'value', 'is_paid']
		


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
	pass
