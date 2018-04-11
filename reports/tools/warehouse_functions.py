
from django.shortcuts import render, HttpResponseRedirect

from reports.tools.general_fuctions import *




def warehouse_get_filters_data(request):
    category_name = request.GET.getlist('category_name', None)
    vendor_name = request.GET.getlist('vendor_name', None)
    site_status = request.GET.get('site_status', None)
    color_name = request.GET.getlist('color_name', None)
    size_name = request.GET.getlist('size_name', None)
    discount_name = request.GET.get('discount_name', None)
    qty_name = request.GET.get('qty_name', None)
    search_name = request.GET.get('search_pro', None)
    return [category_name, vendor_name, color_name, discount_name, qty_name]


def warehouse_filters_data(request, filters, queryset):
    category_name, vendor_name, color_name, discount_name, qty_name = filters
    try:
        queryset = queryset
    except:
        queryset = queryset
    return queryset
    

def warehouse_filters(request, products):
    category_name = request.GET.getlist('category_name', None)
    vendor_name = request.GET.getlist('vendor_name', None)
    site_status = request.GET.get('site_status', None)
    color_name = request.GET.getlist('color_name', None)
    size_name = request.GET.getlist('size_name', None)
    discount_name = request.GET.get('discount_name', None)
    qty_name = request.GET.get('qty_name', None)
    try:
        products = products.filter(qty__gt=0) if qty_name else products
        products = products.filter(price_discount__gt=1) if discount_name else products
        products = products.filter(color__id__in=color_name) if color_name else products
        products = products.filter(category__id__in=category_name) if category_name else products
        products = products.filter(supply__id__in=vendor_name) if vendor_name else  products
        products = products.filter(status__in=site_status) if site_status else products
        size_attr = SizeAttribute.objects.filter(product_related__in=products, title__id__in=size_name)
        products_with_size = [ele.product_related.id for ele in size_attr]
    except:
        pass
    #products = products.filter(id__in=products_with_size)
    query = request.GET.get('search_pro')
    if query:
        products = products.filter(
            Q(title__icontains=query)|
            Q(category__title__icontains=query) |
            Q(supply__title__icontains=query) |
            Q(order_code__icontains=query)
        ).distinct()
    return [products, category_name, vendor_name, color_name, discount_name, qty_name]

def vendor_page_search_products(request, products):
    pass