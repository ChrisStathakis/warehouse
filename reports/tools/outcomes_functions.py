from django.db.models import Q, F,Sum
from point_of_sale.models import RetailOrderItem
from ..reports_tools import diff_month
import datetime

from dateutil.relativedelta import relativedelta


def order_items_filter(request, order_items, order_items_previous_period, orders_items_last_year ):
    if request.GET:
        date_pick = request.GET.get('date_pick')
        category = request.GET.getlist('category')
        category_site = request.GET.getlist('category_site')
        vendor_name = request.GET.getlist('vendor')
        site_status = request.GET.get('site_status')
        ware_status = request.GET.get('ware_status')
        btwob = request.POST.get('btwob_status')
        if date_pick:
            try:
                date_range = date_pick.split('-')
                date_range[0] = date_range[0].replace(' ', '')
                date_range[1] = date_range[1].replace(' ', '')
                date_start = datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
                date_end = datetime.datetime.strptime(date_range[1], '%m/%d/%Y')
                order_items = RetailOrderItem.objects.filter(order__day_added__range=[date_start, date_end])
                days = date_end - date_start
                previous_period_start = date_start - relativedelta(days=days.days)
                previous_period_end = date_start - relativedelta(days=1)
                previous_period = '%s - %s' % (str(previous_period_end).split(' ')[0].replace('-', '/'),
                                               str(previous_period_start).split(' ')[0].replace('-', '/'))
                order_items_previous_period = RetailOrderItem.objects.filter(
                    order__day_created__range=[previous_period_start,
                                               previous_period_end + relativedelta(days=1)]).order_by('-day_added')
                last_year_start = date_start - relativedelta(years=1)
                last_year_end = date_end - relativedelta(years=1)
                orders_items_last_year = RetailOrderItem.objects.filter(
                    order__day_created__range=[last_year_start, last_year_end]).order_by('-day_added')
            except:
                pass
        if vendor_name:
            order_items = order_items.filter(title__supplier__title__in=vendor_name)
            order_items_previous_period = order_items_previous_period.filter(title__supplier__title__in=vendor_name)
            orders_items_last_year = orders_items_last_year.filter(title__supplier__title__in=vendor_name)
        if category_site:
            order_items = order_items.filter(title__category_site__title__in=category_site)
            order_items_previous_period = order_items_previous_period.filter(
                title__category_site__title__in=category_site)
            orders_items_last_year = orders_items_last_year.filter(title__category_site__title__in=category_site)
        if category:
            order_items = order_items.filter(title__category__title__in=category)
            order_items_previous_period = c.filter(title__category__title__in=category)
            orders_items_last_year = orders_items_last_year.filter(title__category__title__in=category)
        if site_status:
            order_items = order_items.filter(status__in=site_status)
            order_items_previous_period = order_items_previous_period.filter(status__in=site_status)
            orders_items_last_year = orders_items_last_year.filter(status__in=site_status)
        if ware_status:
            order_items = order_items.filter(ware_active=ware_status)
            order_items_previous_period = order_items_previous_period.filter(ware_active=ware_status)
            orders_items_last_year = orders_items_last_year.filter(ware_active=ware_status)
        if btwob:
            order_items = order_items.filter(carousel=btwob)
            orders_items_last_year = orders_items_last_year.filter(carousel=btwob)
            order_items_previous_period = order_items_previous_period.filter(carousel=btwob)
    return [order_items, order_items_previous_period, orders_items_last_year]


def outcome_analysis_per_month(date_start, date_end, orders, last_year_orders):
    last_year = datetime.datetime.now() - relativedelta(years=1)
    months = diff_month(date_start, date_end) + 1
    get_data, last_year_data = [], []
    for month in range(months):
        new_date = (date_end - relativedelta(months=month))
        string_month, month, year = new_date.strftime('%B'), new_date.month, new_date.year
        get_orders = orders.filter(day_created__month=month, day_created__year=year).aggregate(Sum('total_price'))[
            'total_price__sum']
        get_orders = get_orders if get_orders else 0
        get_data.append((string_month, get_orders))
        get_last_year_orders = last_year_orders.filter(day_created__month=month, day_created__year=last_year.year).aggregate(Sum('total_price'))[
            'total_price__sum']
        get_last_year_orders = get_last_year_orders if get_last_year_orders else 0
        last_year_data.append((string_month, get_last_year_orders))
    get_data.reverse()
    return get_data, last_year_data


def bills_analysis_per_month(date_start, date_end, orders, last_year_orders):
    last_year = datetime.datetime.now() - relativedelta(years=1)
    months = diff_month(date_start, date_end) + 1
    get_data, last_year_data = [], []
    for month in range(months):
        new_date = (date_end - relativedelta(months=month))
        string_month, month, year = new_date.strftime('%B'), new_date.month, new_date.year
        get_orders = orders.filter(date_expired__month=month, date_expired__year=year).aggregate(Sum('price'))[
            'price__sum']
        get_orders = get_orders if get_orders else 0
        get_data.append((string_month, get_orders))
        get_last_year_orders = last_year_orders.filter(date_expired__month=month, date_expired__year=last_year.year).aggregate(Sum('price'))[
            'price__sum']
        get_last_year_orders = get_last_year_orders if get_last_year_orders else 0
        last_year_data.append((string_month, get_last_year_orders))
    get_data.reverse()
    return get_data, last_year_data


def salary_analysis_per_month(date_start, date_end, orders, last_year_orders):
    last_year = datetime.datetime.now() - relativedelta(years=1)
    months = diff_month(date_start, date_end) + 1
    get_data, last_year_data = [], []
    for month in range(months):
        new_date = (date_end - relativedelta(months=month))
        string_month, month, year = new_date.strftime('%B'), new_date.month, new_date.year
        get_orders = orders.filter(date_expired__month=month, date_expired__year=year).aggregate(Sum('value'))[
            'value__sum']
        get_orders = get_orders if get_orders else 0
        get_data.append((string_month, get_orders))
        get_last_year_orders = last_year_orders.filter(date_expired__month=month, date_expired__year=last_year.year).aggregate(Sum('value'))[
            'value__sum']
        get_last_year_orders = get_last_year_orders if get_last_year_orders else 0
        last_year_data.append((string_month, get_last_year_orders))
    get_data.reverse()
    return get_data, last_year_data


def get_outcomes_filter_data(request):
    bills_name, bills_group_name = request.GET.getlist('bills_name', None), request.GET.getlist(
        'bills_group_name', None)
    search_name = request.GET.get('search_name', None)
    paid_name = request.GET.get('paid_name', None)
    return [bills_name, bills_group_name, search_name, paid_name]


def outcomes_filter_queryset(request, queryset):
    bills_name, bills_group_name, search_name, paid_name = get_outcomes_filter_data(request)
    try:
        queryset = queryset.filter(category__id__in=bills_name) if bills_name else queryset
        queryset = queryset.filter(category__category__id__in=bills_group_name) if bills_group_name else queryset
        queryset = queryset.filter(title__icontains=search_name) if search_name else queryset
        queryset = queryset.filter(is_paid=True) if paid_name == '0' else queryset.filter(is_paid=False) \
            if paid_name == '1' else queryset
    except:
        pass
    return queryset


def filters_payroll(request):
    search_name = request.GET.get('search_name', None)
    payment_name = request.GET.getlist('payment_name', None)
    paid_name = request.GET.get('paid_name', None)
    occup_name = request.GET.getlist('occup_name', None)
    person_name = request.GET.getlist('person_name', None)
    store_name = request.GET.getlist('store_name', None)
    cate_name = request.GET.getlist('cate_name', None)
    return [search_name, payment_name, paid_name, occup_name, person_name, store_name, cate_name]


def filter_payroll_invoice_queryset(request, queryset):
    search_name, payment_name, paid_name, occup_name, person_name, store_name, cate_name = filters_payroll(request)
    try:
        queryset = queryset.filter(is_paid=False) if paid_name else queryset
        queryset = queryset.filter(person__id__in=person_name) if person_name else queryset
        queryset = queryset.filter(person__occupation__id__in=occup_name) if occup_name else queryset
        queryset = queryset.filter(category__in=cate_name) if cate_name else queryset

    except:
        queryset = queryset
    return queryset
