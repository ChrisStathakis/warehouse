from django.contrib import admin
from .models import CostumerAccount, ExtendsUser
# Register your models here.


class CostumerAccountAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'user', 'phone', 'cellphone', 'is_retail', 'is_eshop', 'balance',]
    list_filter = ['is_eshop', 'is_retail']
    search_fields = ['last_name', 'first_name', 'user', 'phone', 'phone1', 'shipping_city', 'shipping_address_1', 'cellphone']
    fieldsets = (
        ('Βασικά Στοιχεία', {
            'fields':(('last_name', 'first_name', 'user'),
                      ('is_retail', 'is_eshop', 'afm', 'DOY'),
                      ('billing_name', 'billing_address', 'billing_city', 'billing_zip_code')),
        }),
        ('Οικονομικά Στοιχεία', {
            'fields': ('balance',),
        }),
        ('Γενικές Πληροφορίες', {
            'fields':(('phone', 'cellphone', 'phone1', 'fax'),
                      ('shipping_address_1', 'shipping_city', 'shipping_zip_code'),)
        })


    )


admin.site.register(CostumerAccount, CostumerAccountAdmin )
admin.site.register(ExtendsUser)

