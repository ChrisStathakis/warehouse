from django.urls import path, include
from .views import *

app_name = 'billings'

urlpatterns = [
    path('home/', BillingPaymentPage.as_view(), name='home'),
    path('list/', BillingPage.as_view(), name='billings'),
    path('home/billings/edit/<int:pk>/', view=billings_invoice_edit, name='edit_bill'),
    path('list/create-category/', CreateBillCategory.as_view(), name='create_bill_cate'),


    path('home/billings/create/', CreateBillPage.as_view(), name='create_bill'),
    path('home/payroll/create/', CreatePayrollPage.as_view(), name='create_payroll'),

    path('home/payroll/list/', PayrollPage.as_view(), name='payroll_page'),
    path('home/payroll/edit-invoice/<int:dk>/', view=edit_payroll_invoice, name='edit_payroll'),
    path('home/payroll/duplicate-invoice/<int:dk>/', view=duplicate_payroll_invoice, name='duplicate_payroll_invoice'),
    path('home/payroll/create-person/', CreatePersonPage.as_view(), name='create_person'),
    path('home/payroll/create-occupation/', CreateOccupPage.as_view(), name='create_occup'),

]