from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import CostumerAccount


class RegisterForm(forms.ModelForm):
    username = forms.CharField(label='Ονοματεπώνυμο')
    email = forms.EmailField(label='Email Address',widget=forms.EmailInput)
    email2 = forms.EmailField(label='Confirm email address', widget=forms.EmailInput)
    # phone = forms.IntegerField(widget=forms.NumberInput)
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput,
                                label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'email2','password', 'password2' ]

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    def clean_email2(self):
        email = self.cleaned_data.get('email')
        email2 = self.cleaned_data.get('email2')
        email_qs = User.objects.filter(email = email)
        if email != email2:
            raise forms.ValidationError('Emails must match!')
        if email_qs.exists():
            raise forms.ValidationError('This email exists!')
        return email

    def clean_password2(self):
        password = self.cleaned_data['password']
        password2 = self.cleaned_data['password2']

        if password != password2:
            raise forms.ValidationError('The passwords dont match!')
        return password


class CreateCostumerFromAdmin(forms.ModelForm):

    class Meta:
        model = CostumerAccount
        fields = '__all__'


class CreateCostumerPosForm(forms.ModelForm):
    is_eshop = forms.BooleanField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = CostumerAccount
        fields =['first_name', 'last_name', 'shipping_address_1', 'shipping_city','phone','cellphone', 'is_eshop']


class CostumerProfileForm(forms.ModelForm):

    model = CostumerAccount
    fields =['first_name','last_name']


class LoginForm(forms.Form):
    username_login = forms.CharField(max_length=100, label='Username')
    password_login = forms.CharField(widget=forms.PasswordInput, label='Password')

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get('username_login')
        password = self.cleaned_data.get('password_login')
        if username and password:
            user = authenticate(username=username, password=password)
            get_user = User.objects.filter(username=username)
            if not get_user:
                raise forms.ValidationError('Username is not correct')
            elif not user:
                raise forms.ValidationError('Password is incorrect')
        return super(LoginForm, self).clean(*args, **kwargs)


class CostumerPageEditDetailsForm(forms.ModelForm):
    first_name = forms.CharField(label='Ονομα', required=True, widget=forms.TextInput(attrs={'class':'form-control'}))
    last_name = forms.CharField(label='Επίθετο', required=True, widget=forms.TextInput(attrs={'class':'form-control'}))
    shipping_address_1 = forms.CharField(label='Διεύθυνση Αποστολής', required=True, widget=forms.TextInput(attrs={'class':'form-control'}))
    shipping_city = forms.CharField(label='Πόλη', required=True, widget=forms.TextInput(attrs={'class':'form-control'}))
    shipping_zip_code = forms.IntegerField(label='Ταχυδρομικός Κώδικας', required=True, widget=forms.TextInput(attrs={'class':'form-control'}))
    phone = forms.IntegerField(label='Τηλέφωνο', required=True, widget=forms.TextInput(attrs={'class':'form-control'}))
    phone1 = forms.IntegerField(label='Τηλέφωνο2', widget=forms.TextInput(attrs={'class':'form-control'}))
    cellphone = forms.IntegerField(label='Κινητό', required=True, widget=forms.TextInput(attrs={'class':'form-control'}))

    class Meta:
        model = CostumerAccount
        fields =['first_name', 'last_name', 'shipping_address_1' ,'shipping_city', 'shipping_zip_code', 'phone', 'phone1', 'cellphone']

