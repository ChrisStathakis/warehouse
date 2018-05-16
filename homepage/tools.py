from products.models import Brands, CategorySite, Color, Size, Product
from django.shortcuts import HttpResponse, HttpResponseRedirect


def initial_filter_data(queryset):
    brands_id = queryset.values_list('brand', flat=False)
    brands = Brands.objects.filter(id__in=brands_id)
    categories_id = queryset.values_list('category_site', flat=False)
    categories = CategorySite.objects.filter(id__in=categories_id)
    color_id = queryset.values_list('color', flat=True)
    colors = Color.objects.filter(id__in=color_id)

    return [brands, categories, colors]


def grab_user_filter_data(request):
    brand_name = request.GET.getlist('brand_name')
    category_name = request.GET.getlist('cate_name')
    color_name = request.GET.getlist('color_name')
    return [brand_name, category_name, color_name]


def filter_queryset(queryset, brand_name, cate_name, color_name):
    queryset = queryset.filter(brand__id__in=brand_name) if brand_name else queryset
    queryset = queryset.filter(category_site__id__in=cate_name) if cate_name else queryset
    queryset = queryset.filter(color__id__in=color_name) if color_name else queryset
    return queryset


def queryset_ordering(request, queryset,):
    ordering_list = {'1': '-price',
                     '2': 'title',
                     '3': '-id'
                     }
    choice = request.GET.get('order_by', None)
    order_choice = ordering_list.get(choice, None) if choice else None
    queryset = queryset.order_by('%s' % order_choice) if order_choice else queryset
    return queryset


def europe_cookie(request):
    get_cookie = request.COOKIES.get('europe_cookie', None)


def cookie_set(request):
    response = HttpResponse('set_europe')
    response.set_cookie('europe_cookie', '1')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
