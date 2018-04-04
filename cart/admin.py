from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from .models import *
# Register your models here.


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    pass


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'id_session', 'value', 'user']


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    search_fields = ['product_related__title', 'order_related__id']
    list_filter = ['order_related', 'qty', 'price',]
    list_display = ['product_related', 'order_related', 'qty', 'final_price']


@admin.register(Coupons)
class CouponsAdmin(admin.ModelAdmin):
    list_display = ['title', 'active']
    list_filter = ['active', ]
