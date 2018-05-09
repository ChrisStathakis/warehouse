from django import forms
from .models import *


class ColorForm(forms.ModelForm):

    class Meta:
        model = Color
        fields = '__all__'


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = '__all__'


class ProductPhotoUploadForm(forms.Form):
    image = forms.ImageField()