from django import forms
from .models import *
from products.models import Product, CategorySite, Brands, Color, Size
from mptt.forms import MoveNodeForm
from  mptt.exceptions import InvalidMove


class UpdateProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = [
                  'active', 'size',
                  'title', 'color',
                  'category', 'category_site',
                  'supply', 'brand',
                  'price', 'price_discount',
                  'order_code', 'measure_unit',
                  'qty', 'price_buy',
                  'barcode', 'safe_stock',
                  'site_active', 'is_service',
                  'sku', 'site_text',
                  'slug', 'notes',
                  
                  ]

    def __init__(self, *args, **kwargs):
        super(UpdateProductForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class CreateProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ['active', 'size',
                  'title', 'color',
                  'category', 'category_site',
                  'supply', 'brand',
                  'price', 'price_discount',
                  'order_code', 'measure_unit',
                  'qty', 'price_buy',
                  'barcode','safe_stock',
                  'site_active', 'is_service',

                  'sku', 'site_text',
                  'slug', 'notes'

                  ]

    def __init__(self, *args, **kwargs):
        super(CreateProductForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class CategorySiteForm(forms.ModelForm):

    class Meta:
        model = CategorySite
        fields = ['active', 'show_on_menu',
                  'title', 'image',
                  'meta_description', 'slug',
                  'parent', 'content',
                  ]

    def __init__(self, *args, **kwargs):
        super(CategorySiteForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class BrandsForm(forms.ModelForm):

    class Meta:
        model = Brands
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(BrandsForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class ColorForm(forms.ModelForm):

    class Meta:
        model = Color
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(ColorForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class SizeForm(forms.ModelForm):

    class Meta:
        model = Size
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(SizeForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class PaymentForm(forms.ModelForm):
    object_id = forms.IntegerField(widget=forms.HiddenInput())
    is_expense = forms.BooleanField(widget=forms.HiddenInput())

    class Meta:
        model = PaymentOrders
        fields = ['date_expired', 'value', 'title', 'payment_type', 'bank', 'is_paid', 'content_type', 'object_id']
        exclude = ['date_created', ]

    def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
