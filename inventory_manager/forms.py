from django import forms
from django.db.models import Sum, F
from products.models import *
from .payment_models import *
from inventory_manager.models import *
from decimal import *

from .models import *


class OrderAdminForm(forms.ModelForm):
    old_vendor = None
    new_vendor = None

    class Meta:
        model = Order
        fields = '__all__'

    def clean_paid_value(self):
        paid_value = self.cleaned_data.get('paid_value')
        is_paid = self.cleaned_data.get('is_paid')
        paid_value = self.cleaned_data.get('total_price') if is_paid else paid_value
        return paid_value

    def clean_vendor(self):
        try:
            old_vendor = self.instance.vendor
        except:
            old_vendor = self.cleaned_data.get('vendor')
        new_vendor = self.cleaned_data.get('vendor')
        self.old_vendor, self.new_vendor = old_vendor, new_vendor
        return new_vendor

    def save(self, commit=True):
        data = super(OrderAdminForm, self).save(commit=False)
        data.save()
        new_vendor, old_vendor = self.new_vendor, self.old_vendor
        if old_vendor != new_vendor:
            get_orders = Order.objects.filter(vendor=old_vendor)
            order_value = get_orders.aggregate(Sum('total_price'))['total_price__sum'] if get_orders else 0
            order_paid = get_orders.aggregate(Sum('paid_value'))['paid_value__sum'] if get_orders else 0
            old_vendor.balance = order_value - order_paid
            old_vendor.save()
        get_orders = Order.objects.filter(vendor=new_vendor)
        order_value = get_orders.aggregate(Sum('total_price'))['total_price__sum'] if get_orders else 0
        order_paid = get_orders.aggregate(Sum('paid_value'))['paid_value__sum'] if get_orders else 0

        new_vendor.balance = order_value - order_paid
        new_vendor.save()
        return data


class OrderItemAdminForm(forms.ModelForm):
    old_product = None
    new_product = None

    class Meta:
        model = OrderItem
        fields = "__all__"

    def clean_price(self):
        get_price = self.cleaned_data.get('price', None)
        get_product = self.clean_product()
        return get_price if get_price else get_product.price_buy

    def clean_product(self):
        try:
            old_product = self.instance.product
        except:
            old_product = self.cleaned_data.get('product')
        new_product = self.cleaned_data.get('product')
        self.new_product, self.old_product = new_product, old_product
        return new_product

    def save(self, commit=True):
        data = super(OrderItemAdminForm, self).save(commit=False)
        new_value = self.cleaned_data.get('price')
        print('before', new_value)
        if not new_value:
            new_value = self.old_product.price_buy if self.old_product else None
            print('print', new_value)
        data.save()
        old_product = self.old_product
        new_product = self.new_product
        if old_product != new_product and old_product:
            old_product.qty -= self.cleaned_data.get('qty')
            old_product.save()
            if not new_product.size:
                new_product.qty += self.cleaned_data.get('qty')
                new_product.save()
        return data


class OrderQuickForm(forms.ModelForm):
    date_created = forms.DateTimeField(widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = Order
        fields = ['date_expired', 'title', 'vendor', 'payment_method',]

    def __init__(self, *args, **kwargs):
        super(OrderQuickForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class WarehouseOrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ['date_expired', 'title', 'payment_method', 'total_discount', 'taxes_modifier']

    def __init__(self, *args, **kwargs):
        super(WarehouseOrderForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class VendorQuickForm(forms.ModelForm):

    class Meta:
        model = Vendor
        fields = ['title', ]

    def __init__(self, *args, **kwargs):
        super(VendorQuickForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class OrderItemForm(forms.ModelForm):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), widget=forms.HiddenInput())
    order = forms.ModelChoiceField(queryset=Order.objects.all(), widget=forms.HiddenInput())

    class Meta:
        model = OrderItem
        fields = ['qty', 'price', 'unit', 'discount', 'product', 'order']

    def __init__(self, *args, **kwargs):
        super(OrderItemForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
