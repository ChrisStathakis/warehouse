from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from import_export. admin import ImportExportModelAdmin
from .models import *
from .forms import OrderAdminForm, OrderItemAdminForm

from dashboard.models import PaymentOrders


class PaymentsOrdersInline(GenericTabularInline):
    model = PaymentOrders
    extra = 1


class WarehouseOrderImageInline(admin.TabularInline):
    model = WarehouseOrderImage
    extra = 1


class OrderAdminInline(admin.TabularInline):
    readonly_fields = ['tag_total_clean_price', 'tag_total_final_price']
    model = OrderItem
    extra = 5
    form = OrderItemAdminForm
    fields = ['product', 'unit', 'discount', 'taxes', 'qty', 'price', 'size', 'tag_total_clean_price', 'tag_total_final_price']

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super(OrderAdminInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'product':
            if request._obj_ is not None:
                field.queryset = field.queryset.filter(supply=request._obj_.vendor)
            else:
                field.queryset = field.queryset.none()
        return field


class PaymentMethodAdmin(ImportExportModelAdmin):
    list_display = ['title', 'active', 'for_site', 'ordering', ]
    list_filter = ['for_site', 'active']


class OrderAdmin(ImportExportModelAdmin):
    readonly_fields = ['tag_clean_value', 'tag_value_after_discount', 'tag_total_value', 'tag_paid_value', ]
    list_display = ['title', 'vendor', 'is_paid', 'tag_total_value']
    list_filter = ['vendor', 'is_paid']
    inlines = [OrderAdminInline, WarehouseOrderImageInline, PaymentsOrdersInline ]
    form = OrderAdminForm
    search_fields = ['code',]
    fieldsets = (
        ('Γενικά Στοιχεία', {
            'fields':(('is_paid', 'title', 'vendor',),
                      ('day_created', 'payment_method', 'taxes_modifier', ),
                      )
        }),
        ('Pricing', {
            'fields': (
                ('tag_clean_value', 'total_discount', 'tag_value_after_discount',
                 'tag_total_value', 'tag_paid_value'),
               )
        }),     
    )

    def get_form(self, request, obj=None, **kwargs):
        # just save obj reference for future processing in Inline
        request._obj_ = obj
        return super(OrderAdmin, self).get_form(request, obj, **kwargs)


class OrderItemAdmin(ImportExportModelAdmin):
    list_display = ['product', 'order']
    form = OrderItemAdminForm

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)


admin.site.register(PreOrderStatement)
admin.site.register(PreOrderStatementItem)
admin.site.register(WarehouseOrderImage)

