from django import forms
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