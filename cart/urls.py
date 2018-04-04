from django.contrib import admin
from django.urls import path, include, re_path
from .views import *

app_name = 'cart'

urlpatterns = [
    path('add/<int:dk>/<int:qty>/', view=add_to_cart, name='add'),
    path('delete/<int:dk>/', view=delete_cart_item, name='delete'),
    ]