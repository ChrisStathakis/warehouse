from django.conf.urls import url
from django.urls import path
from .views import *
from .views_warehouse import *
from .views_outcome import *
from .ajax_views import *
from reports.ajax_calls.ajax_warehouse_calls import *
from reports.ajax_calls.ajax_outcomes_calls import *


app_name = 'reports'

urlpatterns = [
    url(r'^$', HomepageReport.as_view(), name='homepage'),
    url(r'warehouse/$', view=homepage, name='warehouse'),

    # warehouse
    url(r'products/$', ReportProducts.as_view(), name='products'),
    url(r'products/(?P<pk>\d+)/', ProductDetail.as_view(), name='products_detail'),
    url(r'vendors/$', Vendors.as_view(), name='vendors'),
    url(r'vendors/(?P<pk>\d+)/$', view=vendor_detail, name='vendor_detail'),
    path('warehouse-categories', view=warehouse_category_reports, name='warehouse_categories'),
    path('warehouse-category/<int:pk>', WarehouseCategoryReport.as_view(), name='warehouse_category_detail'),
    url(r'orders/$', view=warehouse_orders, name='warehouse_orders'),
    path('orders/<int:dk>', view=order_id, name='warehouse_order_detail'),
    url(r'warehouse-products-flow/$', view=warehouse_order_items_movements, name='warehouse_order_items_flow'),

    # incomes
    url(r'incomes/$', view=reports_income, name='reports_income'),
    url(r'incomes/(?P<dk>\d+)/$', view=reports_specific_order, name='retail_order_detail'),
    url(r'income-flow-items/$', RetailItemsFlow.as_view(), name='sell_item_flow'),
    path('incomes/costumers-page/', CostumersReport.as_view(), name='costumers'),

    # outcomes
    url(r'outcome/$', view=outcome, name='outcomes'),
    url(r'outcome/payment-analysis/$',view=payment_analysis,name='payment_analysis'),
    url(r'warehouse-orders/$', WarehouseOrdersReport.as_view(), name='warehouse_orders'),
    path('warehouse-orders/detail/<int:pk>', WarehouseOrderDetail.as_view(), name='warehouser_order_detail'),
    path('bills-and-assets/', BillsAndAssetsPage.as_view(), name='bills_and_assets'),
    path('payroll/', PayrollPage.as_view(), name='payroll_page'),
    path('payroll/person/<int:dk>/', PersonPayrollReport.as_view(), name='payroll_person'),

    #  outcomes_ajax_calls
    path('warehouse/products/ajax-analysis', view=ajax_products_analysis, name='ajax_products_analysis'),
    path('products/ajax-search/', view=ajax_product_search, name='ajax_product_search'),
    path('product/<int:pk>/ajax_analysis', view=ajax_product_detail, name='ajax_product_analysis'),
    path('vendors/ajax_analysis', view=ajax_vendors_page_analysis, name='ajax_vendors_page_analysis'),
    path('warehouse-orders/analyse/', view=ajax_analyse_vendors, name='ajax_analyse_vendors'),
    path('warehouse/products-flow/analysis/', view=ajax_warehouse_product_movement_vendor_analysis, name='ware_pro_flow_analysis'),
    path('warehouse/ajax-outcome/', view=ajax_outcomes, name='ajax_outcomes'),
    path('incomes/store-analysis/', view=ajax_incomes_per_store, name='ajax_incomes_store_analysis'),
    path('balance-sheet/ajax/warehouse-orders', view=ajax_balance_sheet_warehouse_orders, name='ajax_balance_sheet_ware_orders'),
    path('balance-sheet/ajax/payroll', view=ajax_balance_sheet_payroll, name='ajax_balance_sheet_payroll'),

    # analyse
    url(r'isologismos/$', BalanceSheet.as_view(), name='balance_sheet'),

    url(r'category-report/$', view=category_report, name='category_report'),

    url(r'vendors/(?P<dk>\d+)/add/(?P<pk>\d+)/$' ,view=add_to_pre_order, name='vendor_info_add_preorder'),

    url(r'orders/(?P<dk>\d+)/$',view=order_id, name='report_order_id'),
    url(r'orders/reset-payments/(?P<dk>\d+)/$',view=reports_order_reset_payments, name='report_order_edit'),

    url(r'costumer-report-balance/$', view = costumers_accounts_report, name='costumers_reports'),
    url(r'costumer-report-balance/(?P<dk>\d+)/$', view=specific_costumer_account, name='specific_costumer_report'),

    url(r'income/product/(?P<dk>\d+)/$', view=reports_specific_order, name='reports_specific_order'),
    
    path('payments-flow/', PaymentFlow.as_view(), name='payment_flow'),

    
    ]
