"""warehouse URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import logout
from products.utils import create_database
from account.views import register_or_login
from homepage.views import *
from django.conf.urls import url

from point_of_sale.api.views import RetailOrderRetrieveUpdateDestroyApiView, RetailOrderListApiView
from django.conf.urls.static import static

urlpatterns = [
    path('grappelli/', include('grappelli.urls')), # grappelli URLS
    path('admin/', admin.site.urls),
    path('', Homepage.as_view(), name='homepage'),
    path('offer/', OffersPage.as_view(), name='offers_page'),
    path('new_products/', NewProductsPage.as_view(), name='new_products_page'),

    path('search/', SearchPage.as_view(), name='search_page'),
    path('category/<slug:slug>/', CategoryPageList.as_view(), name='category_page'),

    path('brands/', BrandsPage.as_view(), name='brands'),
    url(r'^brands/(?P<slug>[-\w]+)/$', BrandPage.as_view(), name='brand'),

    url(r'^product/(?P<slug>[-\w]+)/$', ProductPage.as_view(), name='product_page'),
    path('cart-page/', CartPage.as_view(), name='cart_page'),
    path('checkout/',  view=checkout_page, name='checkout_page'),

   
    path('cart/', include('cart.urls', namespace='cart')),

    path('profile-page/', view=user_profile_page, name='profile-page'),
    path('eshop-order/<int:dk>', view=order_detail_page, name='order_detail'),
    path('login-page/', register_or_login, name='login_page'),
    path('logout/', logout, {'next_page': '/',}, name='log_out'),


    path('coupon-remove/<int:dk>/', view=delete_coupon, name='remove_coupon'),
    # create database always stay commented if in production

    path('create-warehouse-data/', view=create_database, name='warehouse_database'),
] + [
    # api

    path('api/', RetailOrderListApiView.as_view(), name='api_rest_order'),
    path('api/<int:pk>/',RetailOrderRetrieveUpdateDestroyApiView.as_view(), name='api_resr_order_detail'),


     # admin urls
    path('dashboard/', include('dashboard.urls', namespace='dashboard',)),
    path('reports/', include('reports.urls', namespace='reports',)),
    path('point-of-sale/', include('point_of_sale.urls', namespace='pos',)),
    path('billings/', include('transcations.urls', namespace='billings')),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
