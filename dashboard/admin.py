from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
# Register your models here.
from .models import *


@admin.register(PaymentOrders)
class PaymentOrdersAdmin(ImportExportModelAdmin):
	list_display = ['title', 'date_expired', 'content_object', 'value', 'is_paid']
	
		
@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
	pass
