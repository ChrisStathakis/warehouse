from .views import *
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models.functions import TruncMonth


def ajax_analyse_vendors(request):
    data = dict()
    date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(request)
    vendor_name = request.GET.getlist('vendor_name[]', None)
    current_orders = Order.objects.filter(day_created__range=[date_start, date_end])
    current_orders = current_orders.filter(vendor__id__in=vendor_name) if vendor_name else current_orders
    current_analysis = current_orders.values('vendor__title').annotate(total_sum=Sum('total_price'))

    last_year_start, last_year_end = date_start - relativedelta(year=1), date_end -relativedelta(year=1)
    last_year_orders = Order.objects.filter(day_created__range=[last_year_start, last_year_end])
    last_year_orders = last_year_orders.filter(vendor__id__in=vendor_name) if vendor_name else last_year_orders
    last_year_analysis = current_orders.values('vendor__title').annotate(total_sum=Sum('total_price'))

    context = locals()
    data['test'] = render_to_string(request=request, template_name='report/ajax/vendor_analysis.html', context=context)
    return JsonResponse(data)


def ajax_warehouse_product_movement_vendor_analysis(request):
    data = dict()
    date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(request)
    search_name, payment_name, is_paid_name, vendor_name, category_name, status_name, date_pick = filters_name(
        request)
    warehouse_order_items = get_filters_warehouse_order_items(request, OrderItem.objects.filter(
        order__day_created__range=[date_start, date_end]))
    product_analysis = warehouse_order_items.values('product').annotate(
        total_sum=Sum('total_clean_value')).order_by('-total_sum')
    category_analysis = warehouse_order_items.values('product__supply__title').annotate(total_sum=Sum('total_clean_value'))
    data['product_analysis'] = render_to_string(request=request, template_name='report/ajax/warehouse-product-flow-analysis.html', context={'product_analysis': product_analysis,})
    return JsonResponse(data)


def ajax_incomes_per_store(request):
    data = dict()
    date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(request)
    queryset = RetailOrder.my_query.all_orders_by_date_filter(date_start, date_end)
    queryset, search_name, store_name, seller_name, order_type_name, status_name, is_paid_name, date_pick =\
        retail_orders_filter(request, queryset)
    get_stores = Store.objects.filter(id__in=store_name)
    store_analysis_per_month = []
    for store in get_stores:
        print(store)
        store_sales = queryset.filter(store_related=store)
        sells_data_orders = store_sales.filter(order_type__in=['r', 'e'])
        return_data_orders = store_sales.filter(order_type='b')
        sells_data = sells_data_orders.annotate(month=TruncMonth('date_created')
                                                ).values('month').annotate(total_incomes=Sum('final_price'),
                                                                           total_cost=Sum('total_cost'),
                                                                           ).order_by('month')
        return_data = return_data_orders.annotate(month=TruncMonth('date_created')
                                                  ).values('month').annotate(total_incomes=Sum('final_price'),
                                                                           total_cost=Sum('total_cost')
                                                                           ).order_by('month')

        store_analysis_per_month.append([store, sells_data, return_data, 0])
    # last year
    last_year_start, last_year_end = date_start - relativedelta(years=1), date_end - relativedelta(years=1)
    print(last_year_start, last_year_end)
    last_queryset = RetailOrder.my_query.all_orders_by_date_filter(last_year_start, last_year_end)
    print(last_queryset.count())
    last_queryset, search_name, store_name, seller_name, order_type_name, status_name, is_paid_name, date_pick =\
        retail_orders_filter(request, last_queryset)
    get_stores = Store.objects.filter(id__in=store_name)
    print(last_queryset.count())
    last_store_analysis_per_month = []
    for store in get_stores:
        store_sales = last_queryset.filter(store_related=store)
        sells_data_orders = store_sales.filter(order_type__in=['r', 'e'])
        return_data_orders = store_sales.filter(order_type='b')
        sells_data = sells_data_orders.annotate(month=TruncMonth('date_created')
                                                ).values('month').annotate(total_incomes=Sum('final_price'),
                                                                           total_cost=Sum('total_cost'),
                                                                           ).order_by('month')
        return_data = return_data_orders.annotate(month=TruncMonth('date_created')
                                                  ).values('month').annotate(total_incomes=Sum('final_price'),
                                                                           total_cost=Sum('total_cost')
                                                                           ).order_by('month')

        last_store_analysis_per_month.append([store, sells_data, return_data, 0])

    context = locals()
    data['store_analysis_per_month'] = render_to_string(request=request,
                                                        template_name='report/ajax/ajax_incomes_per_store.html',
                                                        context=context
                                                        )
    return JsonResponse(data)

@staff_member_required
def ajax_balance_sheet_warehouse_orders(request):
    data = dict()
    date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(request)
    warehouse_orders = Order.objects.filter(day_created__range=[date_start, date_end])
    vendor_analysis = warehouse_orders.values('vendor__title').annotate(total_cost=Sum('total_price'),
                                                                        total_paid=Sum('paid_value'),
                                                                        ).order_by('-total_cost')
    print(vendor_analysis)
    context = locals()
    data['vendor_analysis'] = render_to_string(request=request, template_name='report/ajax/balance_sheet_warehouse_orders.html', context=context)
    return JsonResponse(data)


@staff_member_required
def ajax_balance_sheet_payroll(request):
    data = dict()
    date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(request)
    payroll_orders = PayrollInvoice.objects.filter(date_expired__range=[date_start, date_end])
    get_type = request.GET.get('request_type', None)
    data_analysis = payroll_orders.values('person__title').annotate(total_cost=Sum('value')
                                                                        ).order_by('-total_cost')
    if get_type == 'occupation':
        data_analysis = payroll_orders.values('person__occupation__title').annotate(total_cost=Sum('value')
                                                                        ).order_by('-total_cost')
    context = locals()
    data['payroll_analysis'] = render_to_string(request=request, template_name='report/ajax/ajax_payroll_balance_sheet.html', context=context)
    return JsonResponse(data)


@staff_member_required
def ajax_vendor_detail_product_analysis(request):
    data = {}


@staff_member_required
def ajax_retail_orders_payment_analysis(request):
    data = dict()
    date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(request)
    queryset = RetailOrder.my_query.sells_orders(date_start, date_end)
    queryset, search_name, store_name, seller_name, order_type_name, status_name, is_paid_name, date_pick = \
            retail_orders_filter(request, queryset)
    data_analysis = queryset.values('payment_method__title').annotate(total_data=Sum('final_price')).order_by('total_data')
    context = locals()
    data['payment_analysis'] = render_to_string(request=request,
                                                template_name='report/ajax/retail_analysis.html',
                                                context=context,
                                                )
    return JsonResponse(data)
                