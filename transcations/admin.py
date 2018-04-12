from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from import_export.admin import ImportExportModelAdmin

from .models import *
from .forms import *

# Register your models here.


def fixed_cost_invoice_paid(modeladmin, request, queryset):
    for ele in queryset:
        ele.is_paid = True
        ele.save()
fixed_cost_invoice_paid.short_description = "Πληρωμή"


def paid_action_payroll(modeladmin, request, queryset):
    queryset.update(is_paid=True)
    for ele in queryset:
        ele.is_paid = True
        ele.save()
paid_action_payroll.short_description = 'Πληρωμή'


def payroll_invoice_paid(modeladmin, request, queryset):
    for ele in queryset:
        ele.is_paid = True
payroll_invoice_paid.short_description = "Πληρωμή"


def mass_active(modeladmin, request, queryset):
    queryset.update(active=True)
mass_active.short_description = "Ενεργοποίηση"


def mass_de_active(modeladmin, request, queryset):
    queryset.update(active=False)
mass_de_active.short_description = "Απενεργοποίηση"


class PaymentOrdersInline(GenericTabularInline):
    model = PaymentOrders
    extra = 1
    exclude = ['is_expense', ]


class FixedCostInvoicesInline(admin.TabularInline):
    readonly_fields = ['date_created', ]
    model = FixedCostInvoice
    extra = 1
    per_page = 1
    fields = ['date_expired', 'is_paid', 'title', 'price', 'paid_value', 'payment_method']


@admin.register(FixedCosts)
class FixedCost(ImportExportModelAdmin):
    pass


@admin.register(FixedCostsItem)
class FixedCostsItemAdmin(ImportExportModelAdmin):
    readonly_fields = ['tag_balance', ]
    list_display = ['title', 'category', 'tag_balance']
    list_filter = ['category']


@admin.register(FixedCostInvoice)
class FixedCostInvoiceAdmin(ImportExportModelAdmin):
    save_as = True
    actions = [fixed_cost_invoice_paid, ]
    readonly_fields = ['tag_price', 'date_created', 'tag_paid_value' ]
    list_display = ['date_expired', 'category', 'title', 'tag_price', 'payment_method', 'is_paid']
    list_filter = ['date_expired', 'category', 'is_paid', 'payment_method']
    form = FixedCostInvoiceForm
    inlines = [PaymentOrdersInline, ]
    fieldsets = (
        ('General Info', {
            'fields': (
                ('is_paid', 'title', 'category'),
                
                ('date_created', 'date_expired'),
                ),
        }),
        ('Prices', {
            'fields': (('payment_method', 'final_price', 'tag_paid_value'),),
        }),
        
    )


@admin.register(Occupation)
class OccupationAdmin(ImportExportModelAdmin):
    pass


@admin.register(Person)
class PersonAdmin(ImportExportModelAdmin):
    actions = [mass_active, mass_de_active]
    readonly_fields = ['tag_balance']
    list_display = ['title', 'store_related', 'phone', 'phone1', 'occupation', 'tag_balance', 'active']
    list_filter = ['occupation', 'active', 'store_related']


@admin.register(PayrollInvoice)
class PayrollInvoiceAdmin(ImportExportModelAdmin):
    search_fields = ['title', 'person__title']
    actions = [paid_action_payroll, ]
    save_as = True
    readonly_fields = ['date_created', 'tag_value', 'tag_paid_value']
    list_display = ['date_expired', 'person', 'category', 'title', 'tag_value', 'is_paid']
    list_filter = ['is_paid', 'person', 'payment_method']
    inlines = [PaymentOrdersInline, ]
    fieldsets = (
        ('General Info', {
            'fields': (
                ('is_paid', 'person', 'title', 'category'),
                
                ('date_created', 'date_expired'),
                ),
        }),
        ('Prices', {
            'fields': (('payment_method', 'value', 'tag_paid_value', ),),
        }),
        
    )