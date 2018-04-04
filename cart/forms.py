from django import forms
from .models import CartItem

from .models import Coupons


class CartItemForm(forms.Form):
    qty = forms.IntegerField(required=True,
                             min_value=1,
                             widget=forms.NumberInput(attrs={'class': 'form-control',
                                                             'placeholder': 1,
                                                             'value': 1,
                                                             }),
                             )


class CouponForm(forms.ModelForm):

    class Meta:
        model = Coupons
        fields = '__all__'
        exclude = ['products', ]

    def __init__(self, *args, **kwargs):
        super(CouponForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

