from django.urls import path, include
from .views import *

app_name = 'billings'

urlpatterns = [
    path('home/', BillingPaymentPage.as_view(), name='home'),
    path('list/', BillingPage.as_view(), name='billings'),

    path('home/billings/create/', CreateBillPage.as_view(), name='create_bill'),
    path('home/payroll/create/', CreatePayrollPage.as_view(), name='create_payroll'),


]