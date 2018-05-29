from ..views import *
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models.functions import TruncMonth
from django.db.models import Sum, Q, F
from django.conf import settings
from ..tools.warehouse_functions import warehouse_filters

from inventory_manager.models import Order, OrderItem
from point_of_sale.models import RetailOrderItem
from products.models import Product, Vendor, Category, CategorySite

CURRENCY = settings.CURRENCY

def ajax_products_analysis(request):
    data = dict()
    switcher = request.GET.get('analysis')
    queryset = Product.my_query.active_warehouse()
    queryset = Product.filters_data(request, queryset)
    queryset_analysis = [0, 0, 0] # total_qty, #total_warehouse_value, #total_sell_value
    if switcher == 'warehouse_analysis':
        queryset_analysis[0] = queryset.aggregate(Sum('qty'))['qty__sum'] if queryset else 0
        queryset_analysis[1] = queryset.aggregate(total=Sum(F('qty') * F('price_buy')))['total'] if queryset else 0
        queryset_analysis[2] = queryset.aggregate(total=Sum(F('qty') * F('final_price')))['total'] if queryset else 0
        data['results'] = render_to_string(request=request,
                                           template_name='report/ajax/warehouse/ajax_warehouse_analysis.html',
                                           context={'queryset_analysis': queryset_analysis,
                                                    'currency': CURRENCY,
                                                    'switcher': switcher
                                                    }
                                            )
    if switcher == 'vendor_analysis':
        vendor_analysis = queryset.values('supply__title').annotate(total_ware_price=Sum(F('qty')*F('final_price')),
                                                                    total_sell_price=Sum(F('qty')*F('price_buy'))
                                                                    ).order_by('supply__title')
        data['results'] = render_to_string(request=request,
                                           template_name='report/ajax/warehouse/ajax_warehouse_analysis.html',
                                           context={'vendor_analysis': vendor_analysis,
                                                    'currency': CURRENCY,
                                                    'switcher': switcher,
                                                    }
                                           )
    if switcher == "sells_analysis":
        sells_items = RetailOrderItem.objects.filter(title__in=queryset) if queryset else None
        sells_analysis = sells_items.values('title__title').annotate(total_sells=Sum(F('qty')),
                                                                     incomes=Sum(F('qty')*F('final_price'))
                                                                     ).order_by('-incomes')[:30]
        data['results'] = render_to_string(request=request,
                                          template_name='report/ajax/warehouse/ajax_warehouse_analysis.html',
                                          context={ 'sells_analysis': sells_analysis,
                                                    'currency': CURRENCY,
                                                    'switcher': switcher
                                                  }
                                          )
    if switcher == 'buy_analysis':
        pass
    
    return JsonResponse(data)


def ajax_product_search(request):
    data = dict()
    get_search_name = request.GET.get('search_pro')
    print(len(get_search_name))
    if len(get_search_name) > 2:
        print(get_search_name)
        queryset = Product.my_query.active_warehouse()
        queryset, category_name, vendor_name, color_name, discount_name, qty_name = warehouse_filters(request, queryset)
        data['result_data'] = render_to_string(request=request,
                                               template_name='report/ajax/warehouse/ajax_product_search.html',
                                               context={'queryset': queryset[:5]}
                                            )
    return JsonResponse(data)


def ajax_product_detail(request, pk):
    data = dict()
    product, currency = Product.objects.get(id=pk), CURRENCY
    date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(request)
    switch, context = request.GET.get('switch'), {}
    if switch == 'buy':
        queryset = OrderItem.objects.filter(product=product,
                                            order__date_created__range=[date_start, date_end])
        month_analysis = queryset.annotate(month=TruncMonth('order__date_created')).values('month')\
            .annotate(total_qty=Sum('qty'), total_cost=Sum('total_clean_value'))
        context.update(locals())
    data['results'] = render_to_string(request=request,
                                       template_name='report/ajax/warehouse/ajax_product_detail_analysis.html',
                                       context=context)
    return JsonResponse(data)


def ajax_vendors_page_analysis(request):

    data = dict()
    queryset = Supply.objects.all()
    vendor_name, balance_name, search_pro, queryset = vendors_filter(request, queryset)
    date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(request)

    if request.GET.get('choice') == 'month':
        orders = Order.objects.filter(date_created__range=[date_start, date_end], vendor__id__in=vendor_name)
        month_data = orders.annotate(month=TruncMonth('date_created')).values('month')\
            .annotate(total_cost=Sum('total_price'),
                      total_paid=Sum('paid_value'))
        data['content'] = render_to_string(request=request,
                                           template_name='report/ajax/warehouse/vendors_analysis.html',
                                           context={'month_data': month_data,
                                                    'currency': CURRENCY
                                                    }
                                           )
    return JsonResponse(data)



    
def ajax_vendor_detail_remaining_value(request, pk):
    instance = get_object_or_404(Supply, id=pk)
    data = dict()
    queryset = Product.objects.filter(supply=instance)
    queryset = queryset.exclude(brand__title=False)
    
    total_buy_value = queryset.aggregate(total=Sum(F('price_buy')*F('qty')))['total'] if queryset else 0
    total_sell_value = queryset.aggregate(total=Sum(F('final_price')*F('qty')))['total'] if queryset else 0
    brand_analysis = queryset.values('brand__title').annotate(Sum('qty')).order_by('qty__sum')
   
    brand_analysis = queryset.values('brand__title').annotate(sum_q=Sum('qty'),
                                                              sum_sells=Sum(F('qty')*F('final_price')),
                                                              sum_buys=Sum(F('qty')*F('price_buy')),
                                                            ).order_by('-sum_q')
                                                             
    data['html_data'] = render_to_string(request=request,
                                         template_name = 'report/ajax/warehouse/vendor_analysis_detail.html',
                                         context={
                                                'toal_buy_value': total_buy_value,
                                                'total_sell_value': total_sell_value,
                                                'brand_analysis': brand_analysis,
                                                'currency': CURRENCY,
                                                'instance': instance,
                                                }      
                                         )
    return JsonResponse(data)


def ajax_vendor_sells_analysis(request, pk):
    instance = get_object_or_404(Supply, id=pk)
    date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(request)
    get_products = Product.objects.filter(supply=instance)
    get_sells = RetailOrderItem.objects.filter(title__in=get_products,
                                               order__date_started__range=[date_start, date_end] 
                                               )
    pass
    
    
def ajax_ware_cate_analysis(request):
    data = {}
    products = Product.my_query.active_warehouse()
    