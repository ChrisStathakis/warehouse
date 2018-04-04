from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from import_export.admin import ImportExportModelAdmin
from .models import *
from .forms import *

from dashboard.models import *
from account.models import ExtendsUser
# Register your models here.


def paid_action(modeladmin, request, queryset):
    for order in queryset:
        order.is_paid = True
        order.save()
paid_action.short_description = 'Αποπληρωμή'


class PaymentOrdersInline(GenericTabularInline):
    model = PaymentOrders
    extra = 1


class RetailItemInline(admin.TabularInline):
    model = RetailOrderItem
    readonly_fields = ['tag_total_price', 'tag_final_price']
    extra = 2
    fields = ['title', 'qty', 'tag_final_price', 'is_find', 'tag_total_price', 'size']
    form = RetailOrderItemAdminForm


class RetailOrderAdmin(ImportExportModelAdmin):
    list_display = ['title', 'order', 'qty', 'price', 'size', 'is_find']
    list_filter = ['is_find']
    search_fields = ['title', 'size', 'order']
    form = RetailOrderItemAdminForm


class RetailAdmin(ImportExportModelAdmin):
    save_as = True
    actions = [paid_action, ]
    list_display = ['date_created', 'order_type', 'store_related', 'title', 'status', 'value', 'costumer_account', 'is_paid']
    list_filter =['status', 'order_type', 'payment_method']
    search_fields = ['title', 'costumer_account', ]
    readonly_fields = ['date_edited', 'date_created', 'value', 'tag_final_price', 'total_cost', 'tag_paid_value']
    inlines = [RetailItemInline, PaymentOrdersInline, ]

    form = RetailOrderAdminForm
    fieldsets = (
        ('General Info', {
            'fields': (
                ('is_paid', 'title', 'order_type', ),
                ('payment_method', 'tag_final_price', 'tag_paid_value'),
                ('date_created', 'date_edited'),
                ('costumer_account', 'seller_account', 'store_related')
                ),
        }),
        ('Prices', {
            'fields': (('value', 'discount', 'taxes',), ),
        }),
        ('Eshop Info', {
            'fields': (('status', 'last_name', 'email'),
                       ('address', 'city', 'state', 'zip_code'),
                       ('phone', 'cellphone'),

                       ),
        }),
        ('Warehouse', {
            'fields': (
                ('total_cost',),
                ),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super(RetailAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['seller_account'].queryset = User.objects.filter(is_staff=True)
        return form

    def get_changeform_initial_data(self, request):
        context = {}
        if request.user:
            context['seller_account'] = request.user
            get_extend_user = ExtendsUser.objects.get(user=request.user)
            if get_extend_user:
                context['store_related'] = get_extend_user.store_related
        return context


class ShippingAdmin(admin.ModelAdmin):
    list_filter = ['for_site', 'active']
    list_display = ['title', 'active', 'for_site', 'ordering']


admin.site.register(RetailOrder, RetailAdmin)
admin.site.register(RetailOrderItem, RetailOrderAdmin)

admin.site.register(Shipping)








