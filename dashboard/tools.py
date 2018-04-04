from django.db.models import Q

def dashboard_product_get_filter_data(request):
    search_name = request.GET.get('search_name', None)
    category_name = request.GET.getlist('cate_name', None)
    brand_name = request.GET.getlist('brand_name', None)
    active_name = request.GET.getlist('active_name', None)
    color_name = request.GET.getlist('color_name', None)
    vendor_name = request.GET.getlist('vendor_name', None)
    order_name = request.GET.get('order_name', None)
    return [search_name, category_name, brand_name, active_name, color_name, vendor_name, order_name]


def dashboard_product_filter_queryset(request, queryset):
    search_name = request.GET.get('search_name', None)
    cate_name = request.GET.getlist('cate_name', None)
    brand_name = request.GET.getlist('brand_name', None)
    active_name = request.GET.getlist('active_name', None)
    color_name = request.GET.getlist('color_name', None)
    vendor_name = request.GET.getlist('vendor_name', None)
    order_name = request.GET.get('order_name', None)

    queryset = queryset.filter(category__id__in=cate_name) if cate_name else queryset
    queryset = queryset.filter(brand__id__in=brand_name) if brand_name else queryset
    queryset = queryset.filter(supply__id__in=vendor_name) if vendor_name else queryset
    queryset = queryset.filter(Q(title__icontains=search_name)).distinct() if search_name else queryset
    queryset = queryset.filter(active=True) if active_name == '1' else queryset

    return queryset