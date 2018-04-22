from django.urls import path, include, re_path
from .views import *

app_name = 'inventory'
urlpatterns =[
    path(r"^/$", "inventory_manager.views.homepage",name='inventory'),
    path('vendor-list'/ VendorPageList.as_view(), name='vendor_list'),

]