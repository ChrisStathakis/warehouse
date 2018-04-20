from django.conf.urls import url
from .views import *
from .api.views import RetailOrderRetrieveUpdateDestroyApiView, RetailOrderListApiView
from django.urls import path

from .views_warehouse import *


app_name = 'pos'

urlpatterns = [
    path('', HomePage.as_view(), name='homepage'),
    path('create-sale/', view=create_new_sales_order, name='create_sale'),
    path('sales/<int:pk>/', view=sales, name='sales'),
    path('sales/<int:pk>/pay-order/', view=order_paid, name='order_paid'),
    path('sales/delete-payment/<int:dk>/<int:pk>/', view=delete_payment_order, name='delete_payment_order'),
    path('sales/delete-order/<int:dk>/', view=delete_order, name='delete_order'),

    #actions
    path('sales/add/<int:dk>/<int:pk>/<int:qty>/', view=add_product_to_order_, name='add_to_order'),

    # return url
    path('create-return/', view=create_return_order, name='create_return_sale'),

    # ajax calls
    path('ajax/sales/search/<int:pk>/', view=ajax_products_search, name='ajax_products_search'),
    path('ajax/sales/<int:dk>/<int:pk>/add', view=ajax_add_product, name='ajax_add_product'),
    path('ajax/sales/<int:dk>/delete', view=ajax_delete_product, name='ajax_delete_product'),
    path('ajax/sales/<int:dk>/edit', view=ajax_edit_product, name='ajax_edit_product'),

    # create costumer
    url(r'^author/create', AuthorCreatePopup, name="AuthorCreate"),
    url(r'^author/(?P<pk>\d+)/edit', AuthorEditPopup, name="AuthorEdit"),
    url(r'^author/ajax/get_author_id', get_author_id, name="get_author_id"),

    # create payment
    url(r'^payment/(?P<pk>\d+)/create/', ajax_payment_add, name="PaymentCreate"),
    url(r'^payment/(?P<pk>\d+)/edit', AuthorEditPopup, name="AuthorEdit"),
    url(r'^payment/ajax/get_author_id', get_author_id, name="get_author_id"),

    # warehouse orders urls
    path('warehouse/order-in/create/', view=create_warehouse_income_order, name='warehouse_in_create'),
    path('warehouse/order-in/<int:dk>/', WarehouseOrderInPage.as_view(), name='warehouse_in'),

    # api
    path('api/', RetailOrderListApiView.as_view(), name='api_rest_order'),
    path('api/<int:id>/',RetailOrderRetrieveUpdateDestroyApiView.as_view(), name='api_resr_order_detail'),

    ]
