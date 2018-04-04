from django import forms
from dashboard.constants import PAYMENT_TYPE
from point_of_sale.models import Shipping
from .models import FirstPage, Banner


class PersonalInfoForm(forms.Form):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, label='First Name')
    last_name = forms.CharField(required=True, label='Last Name')

    address = forms.CharField(required=True,)
    city = forms.CharField(required=True)
    zip_code = forms.CharField(required=True, max_length=5, label='Zip Code')

    cellphone = forms.IntegerField(required=True, max_value=9999999999,)
    phone = forms.IntegerField(required=False)

    notes = forms.CharField(required=False, widget=forms.Textarea())

    payment_method = forms.ChoiceField(required=True, choices=PAYMENT_TYPE)
    shipping_method = forms.ModelChoiceField(required=True, queryset=Shipping.objects.all())
    agreed = forms.BooleanField(label='Agree to Terms', required=True)

    def __init__(self, *args, **kwargs):
        super(PersonalInfoForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class FirstPageForm(forms.ModelForm):

    class Meta:
        model = FirstPage
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super(FirstPageForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class BannerForm(forms.ModelForm):
    
    class Meta:
        model = Banner
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super(BannerForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
    

