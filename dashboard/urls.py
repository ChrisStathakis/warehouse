from django.contrib import admin
from django.urls import path, include, re_path
from .views import *
from  .popups_views import createBrandPopup, get_brand_id, createCategoryPopup, create_color_popup
from .views_sells import (EshopOrdersPage, eshop_order_edit, create_eshop_order,
                          add_edit_order_item, edit_order_item, delete_order_item,
                          CartListPage, OrderSettingsPage, print_invoice, 
                          ShippingPage, ShippingEditPage, ShippingCreatePage, delete_shipping,
                          PaymentMethodPage, PaymentMethodCreatePage, PaymentMethodEditPage, delete_payment_method,
                          )
from .views_pages import *
from .user_views import *
from .tools_views import *
from cart.views import create_coupon

from .warehouse_views import *

app_name = 'dashboard'

urlpatterns = [
    path('', DashBoard.as_view(), name='home'),
    path('products/', ProductsList.as_view(), name='products'),
    path('products/create/', ProductCreate.as_view(), name='product_create'),
    path('products/<int:pk>/', view=product_detail, name='product_detail'),
    path('products/add-images/<int:dk>/', ProductAddMultipleImages.as_view(), name='product_add_images'),
    path('products/delete-images/<int:pk>/', view=delete_product_image, name='delete_image'),
    path('products/add-sizes/<int:dk>/', view=product_add_sizechart, name='product_add_sizes'),
    path('products/add-sizes/create/<int:dk>/<int:pk>/', view=create_new_sizechart, name='create_product_sizechart'),

    # popup and ajax calls
    path('products/popup/create-brand/', view=createBrandPopup, name='brand_popup'),
    path('products/popup/create-category/', view=createCategoryPopup, name='category_popup'),
    path('products/popup/get_brand_id/', view=get_brand_id, name='get_brand_id'),
    path('products/popup/create-color/', view=create_color_popup, name='color_popup'),


    path('category/', CategoryPage.as_view(), name='categories'),
    path('categories-site/', CategorySitePage.as_view(), name='categories_site'),
    path('brands/', BrandPage.as_view(), name='brands'),
    path('colors/', ColorPage.as_view(), name='colors'),
    path('sizes/', SizePage.as_view(), name='sizes'),



    #  create urls
    path('category/create/', CategoryCreate.as_view(), name='category_create'),
    path('brands/create/', BrandsCreate.as_view(), name='brands_create'),
    path('colors/create/', ColorCreate, name='color_create'),
    path('sizes/create/', SizeCreate.as_view(), name='size_create'),
    path('category/site/create/', CategorySiteCreate.as_view(), name='category_site_create'),

    #  delete urls
    path('category/delete/<int:pk>/', view=delete_category, name='delete_category'),
    path('brands/delete/<int:pk>/', view=delete_brand, name='delete_brand'),
    path('color/delete/<int:pk>/', view=delete_color, name='delete_color'),

    # edit url
    path('category/detail/<int:pk>/', CategoryDetail.as_view(), name='category_detail'),
    path('category/site/<int:pk>/', CategorySiteEdit.as_view(), name='edit_category_site'),
    path('brands/edit/<int:pk>', view=brandEditPage, name='edit_brand'),
    path('size/edit/<int:pk>', SizeEditPage.as_view(), name='edit_size'),
    path('color/edit/<int:pk>/', ColorEditPage.as_view(), name='edit_color'),


    # redirects
    path('product/copy/<int:pk>/', view=create_copy_item, name='copy_product'),


    #  ajax calls
    path('category/ajax/create/', view=category_create, name='ajax_create_category'),
    path('category/ajax/get_category_id', view=get_category_id, name="ajax_category_id"),



    # order section
    path('eshop-orders/', EshopOrdersPage.as_view(), name='eshop_orders_page'),
    path('eshop-orders/create/',view=create_eshop_order, name='eshop_order_create'),
    path('eshop-orders/edit/<int:pk>/', view=eshop_order_edit, name='eshop_order_edit'),
    path('eshop-orders/add-or-edit/<int:dk>/<int:pk>/<int:qty>/', view=add_edit_order_item, name='add_or_create'),
    path('eshop-orders/edit-order-item/<int:dk>/', view=edit_order_item, name='edit_order_item'),
    path('eshop-orders/delete-order-item/<int:dk>/', view=delete_order_item, name='delete_order_item'),
    path('eshop-orders/print/<int:pk>/', view=print_invoice, name='print_invoice'),

    path('cart-list/', CartListPage.as_view(), name='cart_list'),
    path('order-settings-page/', OrderSettingsPage.as_view(), name='settings_page'),
    path('create-coupon/', view=create_coupon, name='create_coupon'),

    path('warehouse/order/shipping/', ShippingPage.as_view(), name='shipping_view'),
    path('warehouse/order/shipping/detail/<int:pk>/', ShippingEditPage.as_view(), name='shipping_edit_view'),
    path('warehouse/order/shipping/delete/<int:pk>/', view=delete_shipping, name='shipping_delete_view'),
    path('warehouse/order/shipping/create/', ShippingCreatePage.as_view(), name='shipping_create_view'),

    path('warehouse/order/payment-method/', PaymentMethodPage.as_view(), name='payment_view'),
    path('warehouse/order/payment-method/detail/<int:pk>/', PaymentMethodEditPage.as_view(), name='payment_edit_view'),
    path('warehouse/order/payment-method/delete/<int:pk>/', view=delete_payment_method, name='payment_delete_view'),
    path('warehouse/order/payment-method/create/', PaymentMethodCreatePage.as_view(), name='payment_create_view'),

    # user urls
    path('users-list/', UsersPage.as_view(), name='users_list'),


    # page config urls
    path('page-config/', PageConfigView.as_view(), name="page_config"),
    path('page-config/create-banner/', view=create_banner, name='create_banner'),
    path('page-config/edit-banner/<int:dk>/', view=edit_banner_page, name='edit_banner'),
    path('page-config/delete-banner/<int:dk>/', view=delete_banner, name='delete_banner'),

    path('page-config/create-first_page/', view=create_first_page, name='create_first_page'),
    path('page-config/edit-first_page/<int:dk>/', view=edit_first_page, name='edit_first_page'),
    path('page-config/delete-first_page/<int:dk>/', view=delete_first_page, name='delete_first_page'),

] + [
    # warehouse urls
    path('warehouse/home/', WareHouseOrderPage.as_view(), name='warehouse_home'),
    path('warehouse/create-order/', view=create_new_warehouse_order, name='warehouse_create_order'),
    path('warehouse/order/quick-vendor/', view=quick_vendor_create, name='warehouse_quick_vendor'),
    path('warehouse/order/<int:dk>/', view=warehouse_order_detail, name='warehouse_order_detail'),
    path('warehouse/order/add-item/<int:dk>/<int:pk>/', view=warehouse_add_order_item, name='add_order_item'),
    path('warehouse/order/add-item/<int:dk>/edit/', view=edit_order_item, name='edit_order_item'),
    path('warehouse/order/add-item/<int:dk>/delete/', view=delete_order_item, name='delete_order_item'),


]
