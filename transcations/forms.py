from django import forms
from .models import *
from decimal import Decimal


class FixedCostInvoiceForm(forms.ModelForm):
    old_price = 0
    old_paid_value = 0
    new_price = 0
    new_paid_value = 0
    is_paid = False

    class Meta:
        model = FixedCostInvoice
        fields = '__all__'

    def clean_is_paid(self):
        new_data = self.cleaned_data.get('is_paid')
        if new_data:
            self.is_paid = True
        return new_data
            
    def clean_price(self):
        new_price = self.cleaned_data.get('price')
        try:
            old_price = self.instance.price
            if not old_price:
                old_price = 0
        except:
            old_price = 0
        self.old_price, self.new_price = old_price, new_price,
        return new_price

    def clean_paid_value(self):
        new_price = self.cleaned_data.get('paid_value')
        if self.is_paid:
            new_price = self.new_price
        try:
            old_paid_value = self.instance.paid_value
        except:
            old_paid_value = new_price
        self.old_paid_value, self.new_paid_value = old_paid_value, new_price
        return new_price

    def save(self, commit=True):
        data = super(FixedCostInvoiceForm, self).save(commit=False)
        data.save()
        price_diff = self.new_price - self.old_price
        paid_price_diff = self.new_paid_value - self.old_paid_value
        category = self.cleaned_data.get('category')
        category.balance += price_diff-paid_price_diff
        category.save()
        return data


class PayrollInvoiceForm(forms.ModelForm):
    is_paid = False
    old_value = 0
    new_value = 0
    old_paid_value = 0
    new_paid_value = 0

    class Meta:
        model = PayrollInvoice
        fields = '__all__'

    def clean_is_paid(self):
        data = self.cleaned_data.get('is_paid')
        if self.cleaned_data.get('value') <= self.cleaned_data.get('paid_value'):
            data = True
        if data:
            self.is_paid = True
        return data

    def clean_value(self):
        new_value = self.cleaned_data.get('value')
        try:
            old_value = self.instance.value
        except:
            old_value = 0
        self.new_value, self.old_value = new_value, old_value
        return new_value

    def clean_paid_value(self):
        new_value = self.cleaned_data.get('paid_value')
        if self.is_paid:
            new_value = self.cleaned_data.get('value')
        try:
            old_value = self.instance.paid_value
        except:
            old_value = 0
        self.new_paid_value, self.old_paid_value = new_value, old_value
        return new_value

    def save(self, commit=True):
        data = super(PayrollInvoiceForm, self).save(commit=False)
        data.save()
        price_diff = self.new_price - self.old_price
        paid_price_diff = self.new_paid_value - self.old_paid_value
        person = self.cleaned_data.get('person')
        person.balance += price_diff - paid_price_diff
        return data


class CreateBillForm(forms.ModelForm):

    class Meta:
        model = FixedCostInvoice
        fields = '__all__'
        exclude = ['paid_value', 'active', ]

    def __init__(self, *args, **kwargs):
        super(CreateBillForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class CreatePayrollForm(forms.ModelForm):

    class Meta:
        model = PayrollInvoice
        fields = '__all__'
        exclude = ['active']

    def __init__(self, *args, **kwargs):
        super(CreatePayrollForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class CreateBillCategoryForm(forms.ModelForm):

    class Meta:
        model = FixedCostsItem
        fields = '__all__'
        exclude = ['balance',]

    def __init__(self, *args, **kwargs):
        super(CreateBillCategoryForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class CreatePersonForm(forms.ModelForm):

    class Meta:
        model = Person
        fields = '__all__'
        exclude = ['balance',]

    def __init__(self, *args, **kwargs):
        super(CreatePersonForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class CreateOccupForm(forms.ModelForm):

    class Meta:
        model = Occupation
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CreateOccupForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'



class VacationForm(forms.ModelForm):
    date_started = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    date_end = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Vacation
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(VacationForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'