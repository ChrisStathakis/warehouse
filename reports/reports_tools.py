from django.db.models import Q, Sum, F

import datetime
from itertools import chain
from operator import attrgetter
from dateutil.relativedelta import relativedelta

from products.models import SizeAttribute
from point_of_sale.models import *


def initial_data_from_database():
    vendors, categories, categories_site, colors, sizes = [Supply.objects.all(), Category.objects.all(),CategorySite.objects.all(),
                                                           Color.objects.all(), Size.objects.all()]
    return vendors, categories, categories_site, colors, sizes


def initial_date(request, months=3):
    #gets the initial last three months or the session date
    date_now = datetime.datetime.today()
    try:
        date_range = request.session['date_range']
        date_range = date_range.split('-')
        date_range[0] = date_range[0].replace(' ','')
        date_range[1] = date_range[1].replace(' ','')
        date_start = datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
        date_end = datetime.datetime.strptime(date_range[1],'%m/%d/%Y')
    except:
        date_three_months_ago = date_now - relativedelta(months=months)
        date_start = date_three_months_ago
        date_end = date_now
        date_range = '%s - %s' % (str(date_three_months_ago).split(' ')[0].replace('-','/'),str(date_now).split(' ')[0].replace('-','/'))
        request.session['date_range'] = '%s - %s'%(str(date_three_months_ago).split(' ')[0].replace('-','/'),str(date_now).split(' ')[0].replace('-','/'))
    return [date_start, date_end, date_range]


def clean_date_filter(request, date_pick, date_start=None, date_end=None, date_range= None):
    try:
        date_range = date_pick.split('-')
        date_range[0] = date_range[0].replace(' ', '')
        date_range[1] = date_range[1].replace(' ', '')
        date_start = datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
        date_end = datetime.datetime.strptime(date_range[1], '%m/%d/%Y')
        date_range = '%s - %s' % (date_range[0], date_range[1])
    except:
        date_start, date_end, date_range = [date_start, date_end, date_range] if date_start and date_end else \
            initial_date(request)
    return [date_start, date_end, date_range]


def estimate_date_start_end_and_months(request):
    day_now, start_year = datetime.datetime.now(), datetime.datetime(datetime.datetime.now().year, 2, 1)
    date_pick = request.GET.get('date_pick', None)
    start_year, day_now, date_range = clean_date_filter(request, date_pick, date_start=start_year, date_end=day_now)

    # gets the total months of the year
    months_list, month = [], 1
    months = diff_month(start_year, day_now)
    while month <= months + 1:
        months_list.append(datetime.datetime(datetime.datetime.now().year, month, 1).month)
        month += 1
    return [start_year, day_now, date_range, months_list]


def filters_name(request):
    search_name = request.GET.get('search_name', None)
    payment_name = request.GET.getlist('payment_name', None)
    is_paid_name = request.GET.get('is_paid_name', None)
    vendor_name = request.GET.getlist('vendor_name', None)
    category_name = request.GET.getlist('category_name', None)
    status_name = request.GET.getlist('status_name', None)
    date_pick = request.GET.get('date_pick', None)
    return [search_name, payment_name, is_paid_name, vendor_name, category_name, status_name, date_pick]





def payroll_filter_queryset(request, queryset):
    search_name = request.GET.get('search_name', None)
    payment_name = request.GET.getlist('payment_name', None)
    is_paid_name = request.GET.get('is_paid_name', None)
    occup_name = request.GET.getlist('occup_name', None)
    person_name = request.GET.getlist('person_name', None)
    store_name = request.GET.getlist('store_name', None)
    cate_name = request.GET.getlist('cate_name', None)
    queryset = queryset.filter(person__id__in=person_name) if person_name else queryset
    queryset = queryset.filter(store__id__in=store_name) if store_name else queryset
    queryset = queryset.filter(category__in=cate_name) if cate_name else queryset
    queryset = queryset.filter(person__occupation__id__in=occup_name) if occup_name else queryset



def retail_orders_filter(request, queryset):
    search_name = request.GET.get('search_name', None)
    store_name = request.GET.getlist('store_name', None)
    seller_name = request.GET.getlist('seller_name', None)
    order_type_name = request.GET.getlist('order_type_name', None)
    status_name = request.GET.getlist('status_name', None)
    is_paid_name = request.GET.get('is_paid_name', None)
    date_pick = request.GET.get('date_pick', None)
    queryset = queryset.filter(store_related__id__in=store_name) if store_name else queryset
    queryset = queryset.filter(seller_account__id__in=seller_name) if seller_name else queryset
    queryset = queryset.filter(order_type__in=order_type_name) if order_type_name else queryset
    queryset = queryset.filter(status__in=status_name) if status_name else queryset
    queryset = queryset.filter(is_paid=True) if is_paid_name == 'a' else queryset
    queryset = queryset.filter(Q(title__icontains=search_name) |
                               Q(store_related__title__icontains=search_name) |
                               Q(seller_account__username__icontais=search_name) 
        ).distinct() if search_name else queryset
   
    return [queryset, search_name, store_name, seller_name, order_type_name, status_name, is_paid_name, date_pick]


def retail_order_item_filter(request, queryset):
    search_name = request.GET.get('search_name', None)
    store_name = request.GET.getlist('store_name', None)
    seller_name = request.GET.getlist('seller_name', None)
    order_type_name = request.GET.getlist('order_type_name', None)
    status_name = request.GET.getlist('status_name', None)
    is_paid_name = request.GET.get('is_paid_name', None)
    date_pick = request.GET.get('date_pick', None)
    product_name = request.GET.getlist('product_name', None)
    vendor_name = request.GET.getlist('vendor_name', None)
    category_name = request.GET.getlist('category_name', None)
    queryset = queryset.filter(title__id__in=product_name) if product_name else queryset
    queryset = queryset.filter(title__supply__id__in=vendor_name) if vendor_name else queryset
    queryset = queryset.filter(title__category__id__in=category_name) if category_name else queryset
    queryset = queryset.filter(order__store_related__id__in=store_name) if store_name else queryset
    queryset = queryset.filter(order__seller_account__id__in=seller_name) if seller_name else queryset
    queryset = queryset.filter(order__order_type__in=order_type_name) if order_type_name else queryset
    queryset = queryset.filter(order__status__in=status_name) if status_name else queryset
    queryset = queryset.filter(order__is_paid=True) if is_paid_name == 'a' else queryset
    queryset = queryset.filter(Q(order__title__icontains=search_name) |
                               Q(order__store_related__title__icontains=search_name) |
                               Q(order__seller_account__username__icontais=search_name)
                               ).distinct() if search_name else queryset
    return [queryset, search_name, store_name, seller_name, order_type_name, status_name, is_paid_name,
            date_pick,product_name, category_name, vendor_name]


def incomes_analysis(queryset):
    total_incomes, total_paid_value, total_diff, total_cost, total_return, total_sum = 0, 0, 0, 0, 0, 0
    split_data_by_order_type = queryset.values('order_type').annotate(total_incomes=Sum('final_price'),
                                                                      total_cost=Sum('total_cost'),
                                                                      paid_incomes=Sum('paid_value')
                                                                      ).order_by('order_type')
    for ele in split_data_by_order_type:
        total_incomes += ele['total_incomes'] if ele['order_type'] in ['r', 'e'] else 0
        total_paid_value += ele['paid_incomes'] if ele['order_type'] in ['r', 'e'] else 0
        total_cost += ele['total_cost'] if ele['order_type'] in ['r', 'e'] else 0

        total_return += ele['total_incomes'] if ele['order_type'] == 'b' else 0
        total_cost -= ele['total_cost'] if ele['order_type'] == 'b' else 0
        total_paid_value -= ele['paid_incomes'] if ele['order_type'] == 'b' else 0
    total_sum = total_incomes - total_return
    total_diff = total_incomes - total_paid_value
    return [total_incomes, total_paid_value, total_diff, total_cost, total_return, total_sum]
    # stores use annotate malaka


def incomes_analysis_per_month(date_start, date_end, orders,):
    last_year = datetime.datetime.now() - relativedelta(years=1)
    months = diff_month(date_start, date_end) + 1
    get_data, last_year_data = [], []
    for month in range(months):
        new_date = (date_end - relativedelta(months=month))
        string_month, month, year = new_date.strftime('%B'), new_date.month, new_date.year
        get_orders = orders.filter(date_created__month=month, date_created__year=year).aggregate(Sum('final_price'))[
            'final_price__sum'] if orders.filter(date_created__month=month, date_created__year=year) else 0
        get_data.append((string_month, get_orders))
        '''
        get_last_year_orders = last_year_orders.filter(date_created__month=month, date_created__year=last_year.year).aggregate(Sum('final_price'))[
            'final_price__sum'] if last_year_orders.filter(date_created__month=month, date_created__year=last_year.year) else 0
        get_last_year_orders = get_last_year_orders if get_last_year_orders else 0
        last_year_data.append((string_month, get_last_year_orders))
        '''
    get_data.reverse()
    return get_data


def balance_sheet_chart_analysis(start_year, day_now, orders, value):
    get_data = []
    months = diff_month(start_year, day_now)
    string, string_sum = '%s' % value, '%s__sum' % value
    for month in range(months+1):
        new_date = day_now - relativedelta(months=month)
        string_month, month, year = new_date.strftime('%B'), new_date.month, new_date.year
        try:
            get_orders = orders.filter(day_created__month=month, day_created__year=year).aggregate(Sum(string))[
                string_sum] if orders.filter(day_created__month=month, day_created__year=year) else 0
        except:
            get_orders_ = orders.filter(date_created__month=month, date_created__year=year)
            
            get_orders = orders.filter(date_created__month=month, date_created__year=year).aggregate(Sum(string))[
                string_sum] if orders.filter(date_created__month=month, date_created__year=year) else 0
        get_orders = get_orders if get_orders else 0
        get_data.append((string_month, get_orders))
    get_data.reverse()
    return get_data


def balance_sheet_chart_analysis_for_date_expired(start_year, day_now, orders, value):
    get_data = []
    
    months = diff_month(start_year, day_now)
    string, string_sum = '%s' % value, '%s__sum' % value
    for month in range(months+1):
        new_date = day_now - relativedelta(months=month)
        string_month, month, year = new_date.strftime('%B'), new_date.month, new_date.year
        get_orders = orders.filter(date_expired__month=month, date_expired__year=year).aggregate(Sum(string))[
                string_sum] if orders.filter(date_expired__month=month, date_expired__year=year) else 0
        get_orders = get_orders if get_orders else 0
        get_data.append((string_month, get_orders))
    get_data.reverse()
    return get_data


def get_filters_warehouse_order_items(request, queryset):
    search_pro = request.GET.get('search_name', None)
    vendor_name = request.GET.getlist('vendor_name', None)
    category_name = request.GET.getlist('category_name', None)
    category_site_name = request.GET.getlist('category_site_name', None)
    color_name = request.GET.getlist('color_name', None)
    size_name = request.GET.getlist('size_name', None)
    queryset = queryset.filter(product__supply__id__in=vendor_name) if vendor_name else queryset
    queryset = queryset.filter(product__category__id__in=category_name) if category_name else queryset
    queryset = queryset.filter(product__category_site_name__id__in=category_site_name) if category_site_name else queryset
    queryset = queryset.filter(product__color__id__in=color_name) if color_name else queryset
    queryset = queryset.filter(size__in=size_name) if size_name else queryset
    if search_pro:
        queryset = queryset.filter(Q(product__title__icontains=search_pro) |
                                       Q(product__supply__title__icontains=search_pro) |
                                       Q(product__category__title__icontains=search_pro) |
                                       Q(product__category_site__title__icontains=search_pro) |
                                       Q(order__code__icontains=search_pro) |
                                       Q(product__sku__icontains=search_pro)
                                       ).distinct()
    return queryset


def warehouse_vendors_analysis(request, date_start, date_end):
    vendor_name = request.GET.getlist('vendor_name', None)
    orders = Order.objects.filter(day_created__range=[date_start, date_end])
    orders = orders.filter(vendor__id__in=vendor_name) if vendor_name else orders
    current_vendor_analysis = orders.values('vendor__title').annotate(total_value=Sum('total_price'),
                                                                      total_paid_=Sum('paid_value'),
                                                                      )
    print(current_vendor_analysis)
    return [current_vendor_analysis]
#  ------------------

def reports_initial_date(request):
    date_start = datetime.datetime.now().replace(month=1, day=1)
    date_end = datetime.datetime.now()
    date_range = '%s - %s' %(str(date_start).split(' ')[0].replace('-','/'), str(date_end).split(' ')[0].replace('-','/'))
    return [date_start, date_end, date_range]


def split_months(date_start , date_end):
    months_list = []
    month = date_end.month
    months = diff_month(date_start, date_end)
    for ele in range(months+1):
        months_list.append(datetime.datetime(datetime.datetime.now().year, month, 1).month)
        month -= 1
    return months_list


def reports_initial_date(request, months):
    date_now = datetime.datetime.today()
    try:
        date_range = request.session['date_range']
        date_range[0]=date_range[0].replace(' ','')
        date_range[1]=date_range[1].replace(' ','')
        date_start =datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
        date_end =datetime.datetime.strptime(date_range[1],'%m/%d/%Y')

    except:
        date_three_months_ago = date_now - relativedelta(months=months)
        date_start = date_three_months_ago
        date_end = date_now
        request.session['date_range'] = None

    date_range = '%s - %s' %(str(date_start).split(' ')[0].replace('-','/'), str(date_end).split(' ')[0].replace('-','/'))
    return [date_start, date_end, date_range]


def date_pick_session(request):
    date_pick = request.POST.get('date_pick')
    try:
        date_range = date_pick.split('-')
        date_range[0] = date_range[0].replace(' ','')
        date_range[1] = date_range[1].replace(' ','')

        date_start = datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
        date_end = datetime.datetime.strptime(date_range[1], '%m/%d/%Y')
        request.session['date_range'] = '%s --- %s' %(date_start.date(), date_end.date())
        date_range = '%s - %s' %(str(date_start).split(' ')[0].replace('-', '/'), str(date_end).split(' ')[0].replace('-', '/'))
        return [date_start, date_end, date_range]
    except:
        return None


def date_pick_form(request, date_pick): # gets the day form date_pick input and convert it to string its
    if date_pick:
        try:
            date_range = date_pick.split('-')
            date_range[0]=date_range[0].replace(' ','')
            date_range[1]=date_range[1].replace(' ','')
            date_start =datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
            date_end =datetime.datetime.strptime(date_range[1],'%m/%d/%Y')
            request.session['date_range'] = date_pick
            date_end = date_end + relativedelta(days=1)
            return [date_start, date_end]
        except:
            date_pick = None


def diff_month(date_start, date_end):
    return (date_end.year - date_start.year)*12 + (date_end.month - date_start.month)


def vendors_filter(request, queryset):
    vendor_name = request.GET.getlist('vendor_name', None)
    balance_name = request.GET.getlist('balance_name', None)
    query = request.GET.get('search_pro')
    try:
        queryset = queryset.filter(id__in=vendor_name) if vendor_name else queryset
        queryset = queryset.filter(balance__gte=0) if balance_name else queryset
    except:
        queryset = queryset

    return [vendor_name, balance_name, query, queryset]


def product_analysis(products, category_name, vendor_name, color_name):
    category_info = None  # total_qty, #total_warehouse_value, #total_sell_value, diffence in %
    color_info = {}
    vendor_info = {}
    if category_name:
        get_categoties = Category.objects.filter(id__in=category_name)
        category_info = get_categoties.annotate(total_cost=Sum(F('product__price_buy')*F('product__qty')),
                                                count_qty=Sum('product__qty'),
                                                total_sell=Sum(F('product__final_price')*F('product__qty')),

                                               )
    if vendor_name:
        get_vendors = Supply.objects.filter(id__in=vendor_name)
        vendor_info = get_vendors.annotate(total_cost=Sum(F('product__price_buy')*F('product__qty')),
                                           count_qty=Sum('product__qty'),
                                           total_sell=Sum(F('product__final_price')*F('product__qty'))
                                        )

    size_analysis = []
    return [category_info, vendor_info, color_info, size_analysis]


def warehouse_movements_filters(request, date_start, date_end):
    category_name, vendor_name, color_name, size_name, query, date_pick = None, None, None, None, None, None
    products = Product.my_query.active_warehouse()
    sellings, returns, buyings = None, None, None
    if request.GET:
        sellings, returns, buyings = [
            RetailOrderItem.my_query.selling_order_items(date_start=date_start, date_end=date_end),
            RetailOrderItem.my_query.return_order_items(date_start=date_start, date_end=date_end),
            OrderItem.objects.filter(order__day_created__range=[date_start, date_end])
        ]
        ware_all = request.GET.getlist('warehouse_all')
        category_name = request.GET.getlist('category')
        vendor_name = request.GET.getlist('vendor')
        color_name = request.GET.getlist('color_name')
        size_name = request.GET.getlist('size_name')
        query = request.GET.get('search_pro')
        date_pick = request.GET.get('date_pick')
        date_pick_form(request, date_pick=date_pick)
        if ware_all:
            sellings, returns, buyings = [
                RetailOrderItem.my_query.selling_order_items(date_start=date_start, date_end=date_end),
                RetailOrderItem.my_query.return_order_items(date_start=date_start, date_end=date_end),
                OrderItem.objects.filter(order__day_created__range=[date_start, date_end])
            ]
        if date_pick:
            date_start, date_end = date_pick_form(request, date_pick=date_pick)
            sellings = RetailOrderItem.objects.filter(order__day_created__range=[date_start, date_end], order__status__id__in=[6, 7])
            buyings = OrderItem.objects.filter(order__day_created__range=[date_start, date_end])
            returns = RetailOrderItem.my_query.return_order_items(date_start=date_start, date_end=date_end)
        if query:
            products = products.filter(title__contains=query)
            sellings = sellings.filter(
                Q(title__title__contains=query)|
                Q(title__category__title__contains=query) |
                Q(title__supplier__title__contains=query) |
                Q(title__order_code__icontains=query)
            ).distinct()
            buyings = buyings.filter(
                Q(product__title__contains=query)|
                Q(product__category__title__contains=query) |
                Q(product__supplier__title__contains=query) |
                Q(product__order_code__icontains=query)
            ).distinct()
            returns = returns.filter(
                Q(title__title__contains=query)|
                Q(title__category__title__contains=query) |
                Q(title__supplier__title__contains=query) |
                Q(title__order_code__icontains=query)
            ).distinct()
        if category_name:
            products = products.filter(category_site_id__in=category_name)
            buyings = buyings.filter(product__category__id__in=category_name)
            sellings = sellings.filter(title__category__id__in=category_name)
            returns = returns.filter(title__category__id__in=category_name)
        if vendor_name:
            products = products.filter(supplier__id__in=vendor_name)
            buyings = buyings.filter(product__supplier__id__in=vendor_name)
            sellings = sellings.filter(title__supplier__id__in=vendor_name)
            returns = returns.filter(title__supplier__id__in=vendor_name)
        if color_name:
            sellings = sellings.filter(color__title__in=color_name)
            buyings = buyings.filter(product__color_a__title__in=color_name) + buyings.filter(color__title__in = color_name)
        if size_name:
            get_selling = [ele.title for ele in sellings]
            get_returns = [ele.title for ele in returns]
            size_attr = SizeAttribute.objects.filter(product_related__in=get_selling, title__id__in=size_name)
            products_with_size = [ele.product_related.id for ele in size_attr]

    product_movements = sorted(chain(buyings, sellings, returns),
                             key=attrgetter('day_added'),
                             reverse=True)
    return [products, sellings, buyings, returns, product_movements, [category_name, vendor_name, color_name , size_name, query, date_pick]]

def product_movenent_analysis(products_, date_start, date_end, sellings, buyings, returns):
    incomes_per_specific_day, returns_per_specific_day, profit_per_specific_day  = [], [], []
    months = diff_month(date_start, date_end) + 1
    data_per_point = []
    return_per_point = []
    for month in range(months):
        new_date = (date_end - relativedelta(months=month))
        string_month, month, year = new_date.strftime('%B'), new_date.month, new_date.year
        sellings_, returns_, buyings_ = sellings.filter(order__day_created__month=month, order__day_created__year=year),  returns.filter(order__day_created__month=month, order__day_created__year=year), buyings.filter(order__day_created__month=month, order__day_created__year=year)
        orders_incomes_ = sellings_.aggregate(total=Sum(F('price')*F('qty')))['total'] if sellings_.aggregate(total=Sum(F('price')*F('qty')))['total'] else 0
        orders_return_ = returns_.aggregate(Sum('price'))['price__sum'] if returns_.aggregate(Sum('price'))['price__sum'] else 0
        orders_outcome_ = buyings_.aggregate(Sum('price'))['price__sum'] if buyings_.aggregate(Sum('price'))['price__sum'] else 0
        orders_incomes_ -= orders_return_
        data_per_point.append((string_month, orders_incomes_, orders_outcome_))
    products, vendors_stats, color_stats, size_stats, warehouse_cate_stats = {}, {}, {}, {}, {}   #  total_cost_buy ,buy_qty, total_sell, sell_qty
    category_site_stats = {}
    product_analysis = {}
    get_all_vendors = [product.supplier for product in products_ if product.supplier]
    get_all_categories = [product.category for product in products_ if product.category]
    for product in products_:
        total_price_buy = buyings.filter(product=product).aggregate(total=Sum(F('qty')*F('price')))['total'] if buyings.filter(product=product).aggregate(total=Sum(F('qty')*F('price')))['total'] else 0
        buyings_qty = buyings.filter(product=product).aggregate(Sum('qty'))['qty__sum'] if buyings.filter(product=product).aggregate(Sum('qty'))['qty__sum'] else 0
        qty = sellings.filter(title=product).aggregate(Sum('qty'))['qty__sum'] if \
        sellings.filter(title=product).aggregate(Sum('qty'))['qty__sum'] else 0
        total_price = sellings.filter(title=product).aggregate(total=Sum(F('qty') * F('price')))[
                'total'] if sellings.filter(title=product).aggregate(total=Sum(F('qty') * F('price')))[
                'total'] else 0
        products[product] = [total_price_buy, buyings_qty,total_price, qty]
    for supplier in get_all_vendors:
        total_price_buy = buyings.filter(product__supplier=supplier).aggregate(total=Sum(F('qty') * F('price')))['total'] if \
        buyings.filter(product__supplier=supplier).aggregate(total=Sum(F('qty') * F('price')))['total'] else 0
        buyings_qty = buyings.filter(product__supplier=supplier).aggregate(Sum('qty'))['qty__sum'] if \
        buyings.filter(product__supplier=supplier).aggregate(Sum('qty'))['qty__sum'] else 0
        qty = sellings.filter(title__supplier=supplier).aggregate(Sum('qty'))['qty__sum'] if \
            sellings.filter(title__supplier=supplier).aggregate(Sum('qty'))['qty__sum'] else 0
        total_price = sellings.filter(title__supplier=supplier).aggregate(total=Sum(F('qty') * F('price')))[
            'total'] if sellings.filter(title__supplier=supplier).aggregate(total=Sum(F('qty') * F('price')))[
            'total'] else 0
        vendors_stats[supplier] = [total_price_buy, buyings_qty, total_price, qty]
    for category in get_all_categories:
        total_price_buy = buyings.filter(product__category=category).aggregate(total=Sum(F('qty') * F('price')))['total'] if \
        buyings.filter(product__category=category).aggregate(total=Sum(F('qty') * F('price')))['total'] else 0
        buyings_qty = buyings.filter(product__category=category).aggregate(Sum('qty'))['qty__sum'] if \
        buyings.filter(product__category=category).aggregate(Sum('qty'))['qty__sum'] else 0
        qty = sellings.filter(title__category=category).aggregate(Sum('qty'))['qty__sum'] if \
            sellings.filter(title__category=category).aggregate(Sum('qty'))['qty__sum'] else 0
        total_price = sellings.filter(title__category=category).aggregate(total=Sum(F('qty') * F('price')))[
            'total'] if sellings.filter(title__category=category).aggregate(total=Sum(F('qty') * F('price')))[
            'total'] else 0
        warehouse_cate_stats[category] = [total_price_buy, buyings_qty, total_price, qty]
    return [products, vendors_stats, warehouse_cate_stats, color_stats, size_stats, data_per_point]


def category_reports_analysis(initial_order_item_buy, initial_order_item_sell):
    category_info = {}  # qty, total_cost, qty_sell, sell_incomes, qty_return, qty_destroy, destroy_cost, sell_total_cost
    category_site_info = {}  # qty, total_cost, qty_sell, sell_incomes, qty_return, qty_destroy, destroy_cost, sell_total_cost
    for item in initial_order_item_buy:
        if item.product.category not in category_info.keys() and item.product.category:
            category_info[item.product.category] = [item.qty, item.total_value(), 0, 0, 0, 0, 0, 0]
        elif item.product.category:
            get_data = category_info[item.product.category]
            get_data[0] += item.qty
            get_data[1] += item.total_value()
            category_info[item.product.category] = get_data
        if item.product.category_site not in category_site_info.keys() and item.product.category_site:
            if item.product.category_site.is_parent:
                category_site_info[item.product.category_site] = [item.qty, item.total_value(), 0, 0, 0, 0, 0, 0]
            elif item.product.category_site.is_first_born:
                first_born = item.product.category_site.category
                category_site_info[item.product.category_site] = [item.qty, item.total_value(), 0, 0, 0, 0, 0, 0]
                if first_born not in category_site_info.keys():
                    category_site_info[first_born] = [item.qty, item.total_value(), 0, 0, 0, 0, 0, 0]
                else:
                    get_data = category_site_info[first_born]
                    get_data[0] += item.qty
                    get_data[1] += item.total_value()
                    category_site_info[first_born] = get_data
            elif item.product.category_site.is_second_son:
                first_born = item.product.category_site.category
                second_son = item.product.category_site.category.category
                if first_born not in category_site_info.keys():
                    category_site_info[first_born] = [item.qty, item.total_value(), 0, 0, 0, 0, 0, 0]
                else:
                    get_data = category_site_info[first_born]
                    get_data[0] += item.qty
                    get_data[1] += item.total_value()
                    category_site_info[first_born] = get_data

                if second_son not in category_site_info.keys():
                    category_site_info[second_son] = [item.qty, item.total_value(), 0, 0, 0, 0, 0, 0]
                else:
                    get_data = category_site_info[second_son]
                    get_data[0] += item.qty
                    get_data[1] += item.total_value()
                    category_site_info[second_son] = get_data
        elif item.product.category_site:
            if item.product.category_site.is_parent:
                get_data = category_site_info[item.product.category_site]
                get_data[0] += item.qty
                get_data[1] += item.total_value()
                category_site_info[item.product.category_site] = get_data
            elif item.product.category_site.is_first_born:
                parent = item.product.category_site.category
                get_data_parent = category_site_info[parent]
                get_data_parent[0] += item.qty
                get_data_parent[1] += item.total_value()
                category_site_info[parent] = get_data_parent
                get_data = category_site_info[item.product.category_site]
                get_data[0] += item.qty
                get_data[1] += item.total_value()
                category_site_info[item.product.category_site] = get_data
            elif item.product.category_site.is_second_son:
                grand_father = item.product.category_site.category.category
                get_data_grand = category_site_info[grand_father]
                get_data_grand[0] += item.qty
                get_data_grand[1] += item.total_value()
                category_site_info[grand_father] = get_data_grand
                parent = item.product.category_site.category
                get_data_parent = category_site_info[parent]
                get_data_parent[0] += item.qty
                get_data_parent[1] += item.total_value()
                category_site_info[parent] = get_data_parent
                get_data = category_site_info[item.product.category_site]
                get_data[0] += item.qty
                get_data[1] += item.total_value()
                category_site_info[item.product.category_site] = get_data
    for sell in initial_order_item_sell:
        if sell.title.category not in category_info.keys():
            if sell.order.status.id == 7:
                category_info[sell.title.category] = [0, 0, sell.qty, sell.total_price_number(), 0, 0, 0,
                                                      sell.total_cost()]
            if sell.order.status.id == 8:
                category_info[sell.title.category] = [0, 0, 0, 0, abs(sell.qty), abs(sell.total_price_number()), 0, 0]
        else:
            if sell.order.status.id == 7:
                get_data = category_info[sell.title.category]
                get_data[2] += sell.qty
                get_data[3] += sell.total_price_number()
                get_data[7] += sell.total_cost()
                category_site_info[sell.title.category] = get_data
            if sell.order.status.id == 8:
                get_data = category_info[sell.title.category]
                get_data[4] += abs(sell.qty)
                get_data[5] += abs(sell.total_price_number())
                category_site_info[sell.title.category] = get_data
        if sell.order.status.id == 7:
            if sell.title.category_site not in category_site_info.keys() and sell.title.category_site:
                if sell.title.category_site.is_parent:
                    category_site_info[sell.title.category_site] = [0, 0, sell.qty, sell.total_price_number(), 0, 0, 0,
                                                                    sell.total_cost()]
                if sell.title.category_site.is_first_born:
                    parent = sell.title.category_site.category
                    category_site_info[sell.title.category_site] = [0, 0, sell.qty, sell.total_price_number(), 0, 0, 0,
                                                                    sell.total_cost()]
                    if parent not in category_site_info.keys():
                        category_site_info[parent] = [0, 0, sell.qty, sell.total_price_number(), 0, 0, 0,
                                                      sell.total_cost()]
                    else:
                        get_data = category_site_info[parent]
                        get_data[2] += sell.qty
                        get_data[3] += sell.total_price_number()
                        category_site_info[parent] = get_data
                if sell.title.category_site.is_second_child:
                    grand_father = sell.title.category_site.category.category
                    parent = sell.title.category_site.category
                    category_site_info[sell.title.category_site] = [0, 0, sell.qty, sell.total_price_number(), 0, 0, 0,
                                                                    sell.total_cost()]
                    if parent not in category_site_info.keys():
                        category_site_info[parent] = [0, 0, sell.qty, sell.total_price_number(), 0, 0, 0,
                                                      sell.total_cost()]
                    else:
                        get_data = category_site_info[parent]
                        get_data[2] += sell.qty
                        get_data[3] += sell.total_price_number()
                        category_site_info[parent] = get_data
                    if grand_father not in category_site_info.keys():
                        category_site_info[grand_father] = [0, 0, sell.qty, sell.total_price_number(), 0, 0, 0,
                                                            sell.total_cost()]
                    else:
                        get_data = category_site_info[grand_father]
                        get_data[2] += sell.qty
                        get_data[3] += sell.total_price_number()
                        category_site_info[grand_father] = get_data
        if sell.order.status.id == 8:
            if sell.title.category_site not in category_site_info.keys() and sell.title.category_site:
                if sell.title.category_site.is_parent:
                    category_site_info[sell.title.category_site] = [0, 0, 0, 0, abs(sell.qty),
                                                                    abs(sell.total_price_number()), 0, 0]
                if sell.title.category_site.is_first_born:
                    category_site_info[sell.title.category_site] = [0, 0, 0, 0, abs(sell.qty),
                                                                    abs(sell.total_price_number()), 0, 0]
                    parent = sell.title.category_site.category
                    if parent not in category_site_info.keys():
                        category_site_info[parent] = [0, 0, 0, 0, abs(sell.qty), abs(sell.total_price_number()), 0, 0]
                    else:
                        get_data = category_site_info[parent]
                        get_data[4] += abs(sell.qty)
                        get_data[5] += abs(sell.total_price_number())
                        category_site_info[parent] = get_data
                if sell.title.category_site.is_second_child:
                    category_site_info[sell.title.category_site] = [0, 0, 0, 0, abs(sell.qty),
                                                                    abs(sell.total_price_number()), 0, 0]
                    grand_father = sell.title.category_site.category.category
                    if grand_father not in category_site_info.keys():
                        category_site_info[grand_father] = [0, 0, 0, 0, abs(sell.qty), abs(sell.total_price_number()),
                                                            0, 0]
                    else:
                        get_data = category_site_info[grand_father]
                        get_data[4] += abs(sell.qty)
                        get_data[5] += abs(sell.total_price_number())
                        category_site_info[grand_father] = get_data
                    parent = sell.title.category_site.category
                    if parent not in category_site_info.keys():
                        category_site_info[parent] = [0, 0, 0, 0, abs(sell.qty), abs(sell.total_price_number()), 0, 0]
                    else:
                        get_data = category_site_info[parent]
                        get_data[4] += abs(sell.qty)
                        get_data[5] += abs(sell.total_price_number())
                        category_site_info[parent] = get_data
    return [category_info, category_site_info]


def help_initial_data(current_orders):
    incomes = current_orders.filter(order_type__in=['e', 'r']).aggregate(Sum('paid_value'))['paid_value__sum'] if \
    current_orders.filter(order_type__in=['e', 'r']).aggregate(Sum('paid_value'))['paid_value__sum'] else 0
    return_orders = current_orders.filter(order_type='b').aggregate(Sum('value'))['value__sum'] if \
    current_orders.filter(order_type='b').aggregate(Sum('value'))['value__sum'] else 0
    sells_cost = current_orders.aggregate(Sum('total_cost'))['total_cost__sum'] if \
    current_orders.aggregate(Sum('paid_value'))['paid_value__sum'] else 0
    return [incomes - return_orders, sells_cost, incomes - return_orders - sells_cost]


def incomes_table_analysis(current_orders, previous_orders, last_year_orders, filter_type, filter_query):
    current_data , previous_data, last_year_data = {}, {}, {}
    current_data['Συνολο'] = help_initial_data(current_orders)
    previous_data['Συνολο'] = help_initial_data(previous_orders)
    last_year_data['Συνολο'] = help_initial_data(last_year_orders)
    for type in filter_query:
        curr_orders = current_orders.filter(seller_account=type) if filter_type == 'users' else \
                        current_orders.filter(payment_method=type) if filter_type == 'payment' else \
                        current_orders
        incomes = curr_orders.filter(order_type__in=['e', 'r']).aggregate(Sum('paid_value'))['paid_value__sum'] if curr_orders.filter(order_type__in=['e', 'r']).aggregate(Sum('paid_value'))['paid_value__sum'] else 0
        return_orders = curr_orders.filter(order_type='b').aggregate(Sum('value'))['value__sum'] if curr_orders.filter(order_type='b').aggregate(Sum('value'))['value__sum'] else 0
        sells_cost = curr_orders.aggregate(Sum('total_cost'))['total_cost__sum'] if curr_orders.aggregate(Sum('paid_value'))['paid_value__sum'] else 0
        current_data[type] = [incomes - return_orders, sells_cost, incomes- return_orders-sells_cost]
    for type in filter_query:
        curr_orders = previous_orders.filter(seller_account=type) if filter_type == 'users' else current_orders.filter(payment_method=type) if filter_type == 'payment' else current_orders
        incomes = curr_orders.filter(order_type__in=['e', 'r']).aggregate(Sum('paid_value'))['paid_value__sum'] if curr_orders.filter(order_type__in=['e', 'r']).aggregate(Sum('paid_value'))['paid_value__sum'] else 0
        return_orders = curr_orders.filter(order_type='b').aggregate(Sum('value'))['value__sum'] if curr_orders.filter(order_type='b').aggregate(Sum('value'))['value__sum'] else 0
        sells_cost = curr_orders.aggregate(Sum('total_cost'))['total_cost__sum'] if curr_orders.aggregate(Sum('paid_value'))['paid_value__sum'] else 0
        previous_data[type] = [incomes - return_orders, sells_cost, incomes- return_orders-sells_cost]
    for type in filter_query:
        curr_orders = last_year_orders.filter(seller_account=type) if filter_type == 'users' else current_orders.filter(payment_method=type) if filter_type == 'payment' else current_orders
        incomes = curr_orders.filter(order_type__in=['e', 'r']).aggregate(Sum('paid_value'))['paid_value__sum'] if curr_orders.filter(order_type__in=['e', 'r']).aggregate(Sum('paid_value'))['paid_value__sum'] else 0
        return_orders = curr_orders.filter(order_type='b').aggregate(Sum('value'))['value__sum'] if curr_orders.filter(order_type='b').aggregate(Sum('value'))['value__sum'] else 0
        sells_cost = curr_orders.aggregate(Sum('total_cost'))['total_cost__sum'] if curr_orders.aggregate(Sum('paid_value'))['paid_value__sum'] else 0
        last_year_data[type] = [incomes - return_orders, sells_cost, incomes- return_orders-sells_cost]
    return current_data, previous_data, last_year_data





# warehouse outcome tools

def bills_and_expense_tool(model, day_now, year_start,):
    get_bills = model.objects.all().filter(date__range=[year_start, day_now])
    bills_all = get_bills.aggregate(Sum('price'))['price__sum'] if get_bills.aggregate(Sum('price'))[
        'price__sum'] else 0
    bills_paid = get_bills.filter(active='b').aggregate(Sum('price'))['price__sum'] if \
    get_bills.filter(active='b').aggregate(Sum('price'))['price__sum'] else 0
    bills_pending = get_bills.filter(active='a').aggregate(Sum('price'))['price__sum'] if \
    get_bills.filter(active='a').aggregate(Sum('price'))['price__sum'] else 0
    return bills_all, bills_paid, bills_pending


def bills_and_expenses_analytics(category, data):
    bills_analytics = {}
    for bill in category:
        bill_sum = data.filter(category=bill, active='a').aggregate(Sum('price'))
        bill_sum = bill_sum['price__sum']
        bills_analytics[bill.title] = bill_sum
    return bills_analytics
