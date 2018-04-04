from django.shortcuts import HttpResponseRedirect

from .models import *
from string import ascii_letters


def products_filter_queryset(queryset, search_pro):
    new_queryset = queryset.filter()


def create_database(request):
    vendor_size, brand_size, category_size, product_size = 5, 5, 5, 100
    for ele in range(product_size):
        print(ele)
    return HttpResponseRedirect('/reports')