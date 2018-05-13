from django import forms
from django.forms import modelformset_factory
from django.forms import BaseModelFormSet
from .models import *


class ProductCreateForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = '__all__'


class ProductAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ProductAdminForm, self).__init__(*args, **kwargs)
        self.fields['related_products'].queryset = Product.objects.filter(category=self.instance.category)
        self.fields['different_color'].queryset = Product.objects.filter(category=self.instance.category, 
                                                                         brand=self.instance.brand
                                                                         )


class ProductPhotoForm(forms.ModelForm):

    class Meta:
        model = ProductPhotos
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ProductPhotoForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class BaseProductPhotoFormSet(BaseModelFormSet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = ProductPhotos.objects.filter(product=self.model.product)


ProductPhotoFormSet = modelformset_factory(ProductPhotos,
                                           extra=4,
                                           form=ProductPhotoForm,

                                           )


class BrandForm(forms.ModelForm):

    class Meta:
        model = Brands
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(BrandForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class CategorySiteForm(forms.ModelForm):

    class Meta:
        model = CategorySite
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CategorySiteForm, self).__init__(*args, **kwargs)
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


class SizeAttributeForm(forms.ModelForm):

    class Meta:
        model = SizeAttribute
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(SizeAttributeForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


SizeAttributeFormSet = modelformset_factory(SizeAttribute,
                                            fields='__all__',
                                            max_num=10,
                                            extra=10,
                                            form=SizeAttributeForm,
                                            )



class VendorForm(forms.ModelForm):

    class Meta:
        model = Supply
        fields = "__all__"
        exclude = ["date_added",]

    def __init__(self, *args, **kwargs):
        super(VendorForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class SiteAttributeForm(forms.ModelForm):
    
    class Meta:
        model = SizeAttribute
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(SiteAttributeForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget =  forms.HiddenInput()
