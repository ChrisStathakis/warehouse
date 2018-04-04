from django.shortcuts import render, render_to_response, HttpResponseRedirect, redirect
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, F
from django.db.models import ExpressionWrapper, DecimalField
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.template.context_processors import csrf
from django.db.models import Avg, Max, Min, Sum, Count
from django.contrib import messages
from django.views.generic import ListView, DetailView, TemplateView, View

from products.models import *
from products.utils import *
from inventory_manager.models import *
from dashboard.models import PaymentOrders
from dashboard.constants import *
from inventory_manager.payment_models import *
from point_of_sale.models import *
from .reports_tools import  reports_initial_date, date_pick_session, date_pick_form, diff_month
from .tools import *
from transcations.models import *
from reports.reports_tools import *
from .tools.outcomes_functions import order_items_filter
from django.db.models.functions import TruncMonth
from account.models import CostumerAccount

from itertools import chain
from operator import attrgetter
from dateutil.relativedelta import relativedelta
import datetime


MONTHS = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']


def set_session(request):
    try:
        costumer_name = request.session['report_income_costu']
    except:
        request.session['report_income_costu']=None
        costumer_name = None
    try:
        order_type_name = request.session['report_income_type']
    except:
        request.session['report_income_type'] = None
        order_type_name =None
    try:
        shipping_name =request.session['report_income_ship']
    except:
        request.session['report_income_ship'] = None
        shipping_name = None
    try:
        date_pick = request.session['report_income_date']
    except:
        request.session['report_income_date'] = None
        date_pick = None


@method_decorator(staff_member_required, name='dispatch')
class HomepageReport(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(HomepageReport, self).get_context_data(**kwargs)
        retail_orders = RetailOrder.objects.all().order_by('-date_created')[:10]
        warehouse_orders = Order.objects.all().order_by('-date_created')[:10]
        paid_orders = PaymentOrders.objects.all()[:10]
        context.update(locals())
        return context


class HomepageProductWarning(ListView):
    model = Product 
    template_name = ''
    paginate_by = 50
        

@staff_member_required
def reports_income(request):
    title = 'Πωλήσεις'
    # initial data
    date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(request)
    queryset = RetailOrder.my_query.all_orders_by_date_filter(date_start, date_end)
    last_year_start, last_year_end = date_start - relativedelta(years=1), date_end - relativedelta(years=1)
    last_year_queryset = RetailOrder.my_query.sells_orders(last_year_start, last_year_end)

    # filters and initial data
    seller_account, stores = User.objects.filter(is_staff=True), Store.objects.all()
    shipping, payment_methods, order_type_name, order_status, currency = Shipping.objects.all(), PAYMENT_TYPE, \
                                                                         ORDER_TYPES, ORDER_STATUS, CURRENCY
    queryset, search_name, store_name, seller_name, order_type_name, status_name, is_paid_name, date_pick = \
        retail_orders_filter(request, queryset)
    last_year_queryset, search_name, store_name, seller_name, order_type_name, status_name, is_paid_name, date_pick = \
        retail_orders_filter(
        request, last_year_queryset)
    days = date_end - date_start

    # feed the charts
    total_incomes, total_paid_value, total_diff, total_cost, total_return, total_sum = incomes_analysis(queryset)
    current_year_month_analysis = incomes_analysis_per_month(date_start, date_end, queryset)
    last_year_month_analysis = incomes_analysis_per_month(last_year_start, last_year_end, last_year_queryset)
    store_analysis = queryset.values('store_related__title').annotate(country_population=Sum('final_price')).\
        order_by('-country_population')



    # previous range day
    '''
    previous_period_start, previous_period_end = date_start - relativedelta(days=days.days), date_start - relativedelta(days=1)
    previous_period = '%s - %s' % (str(previous_period_end).split(' ')[0].replace('-', '/'),str(previous_period_start).split(' ')[0].replace('-', '/'))
    order_items_previous_period = RetailOrder.objects.filter(status__id=7, day_created__range =[previous_period_start, previous_period_end + relativedelta(days=1)]).order_by('-day_created')
    previous_orders = RetailOrder.my_query.all_orders_by_date_filter(previous_period_start, previous_period_end).filter(order_type__in=['r', 'e'], status__id__in=[7, 8]).order_by('-day_created')
    # creates last year date range
    last_year_start, last_year_end = date_start - relativedelta(years=1), date_end - relativedelta(years=1)
    orders_items_last_year = RetailOrder.objects.filter(status__id__in=[7, 8], day_created__range =[last_year_start, last_year_end]).order_by('-day_created')
    last_year_orders = RetailOrder.my_query.all_orders_by_date_filter(last_year_start, last_year_end).filter(order_type__in=['r', 'e'], status__id__in=[7, 8]).order_by('-day_created')
    # present orders
    orders = all_orders.filter(order_type__in=['r', 'e'], status__id__in=[7, 8]).order_by('-day_created')
    orders_analysis, last_year_analysis = incomes_analysis_per_month(date_start, date_end, orders, last_year_orders)
    total_value, total_incomes, total_remaining_value, sum_product_cost = incomes_analysis(all_orders)
    # average values
    avg_cost, avg_profit, avg_income = 0, 0, 0
    if orders:
        avg_cost = orders.aggregate(Avg('total_cost'))['total_cost__avg']
        avg_income = orders.aggregate(Avg('paid_value'))['paid_value__avg']
        avg_profit = avg_income - avg_cost
    # table analysis
    current_data_per_user, previous_data_per_user, last_data_per_user = incomes_table_analysis(orders, previous_orders, last_year_orders, 'users', users)
    current_data_per_payment, previous_data_per_payment, last_data_per_payment = incomes_table_analysis(orders, previous_orders, last_year_orders, 'payment', payment_methods)
    '''
    paginator = Paginator(queryset, 50)
    page = request.GET.get('page')
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        queryset = paginator.page(1)
    except EmptyPage:
        queryset = paginator.page(paginator.num_pages)
    context = locals()
    context.update(csrf(request))
    return render(request, 'report/incomes.html', context)


@staff_member_required
def reports_specific_order(request, dk):
    currency = CURRENCY
    order = RetailOrder.objects.get(id=dk)
    order_items = order.retailorderitem_set.all()
    return_page = request.META.get('HTTP_REFERER')
    context = locals()
    return render(request, 'report/income_specific_order.html', context)


class RetailItemsFlow(ListView):
    model = RetailOrderItem
    template_name = 'reports/order_item_flow.html'
    paginate_by = 100

    def get_queryset(self):
        date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(self.request)
        queryset = RetailOrderItem.my_query.all_orders_by_date_filter(date_start, date_end)
        queryset, search_name, store_name, seller_name, order_type_name, status_name, is_paid_name,date_pick, \
        product_name, category_name, vendor_name = retail_order_item_filter(self.request, queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(RetailItemsFlow, self).get_context_data(**kwargs)
        currency = CURRENCY
        vendors, categories, categories_site, colors, sizes = initial_data_from_database()
        date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(self.request)
        queryset, search_name, store_name, seller_name, order_type_name, status_name, is_paid_name, date_pick, \
        product_name, category_name, vendor_name = retail_order_item_filter(self.request, self.object_list)

        # table data
        table_results = self.object_list.values('order__order_type').annotate(total_incomes=Sum(F('qty')*F('final_price')),
                                                                       total_cost=Sum(F('qty')*F('cost'))
                                                                       ).order_by('final_price')
        total_incomes, total_returns, total_destroy = [0, 0], [0, 0], [0, 0] # first incomes on list after the cost
        for result in table_results:
            total_incomes[0] += result['total_incomes'] if result['order__order_type'] in ['r', 'e'] else 0
            total_incomes[1] += result['total_cost'] if result['order__order_type'] in ['r', 'e'] else 0
            total_returns[0] += result['total_incomes'] if result['order__order_type'] == 'b' else 0
            total_returns[1] += result['total_cost'] if result['order__order_type'] == 'b' else 0
            total_destroy[0] += result['total_incomes'] if result['order__order_type'] == 'd' else 0
            total_destroy[1] += result['total_cost'] if result['order__order_type'] == 'd' else 0
        total_sum = [total_incomes[0] - total_returns[0], total_incomes[1] - total_returns[1]-total_destroy[1]]
        context.update(locals())
        return context


@staff_member_required
def sell_items_flow(request):
    title = 'Ροή Προϊόντων'
    warehouse_categories, vendors, site_categories, colors, sizes, costumers  = Category.objects.all(), Supply.objects.all(), \
                                                                    CategorySite.objects.all(), Color.objects.all(), \
                                                                                Size.objects.all(), CostumerAccount.objects.all()
    date_start, date_end, date_range = initial_date(request)
    #  initial start
    order_items = RetailOrderItem.objects.filter(order__day_created__range =[date_start, date_end]).order_by('-day_added')
    days = date_end - date_start
    previous_period_start = date_start - relativedelta(days=days.days)
    previous_period_end = date_start - relativedelta(days=1)
    previous_period = '%s - %s'%(str(previous_period_end).split(' ')[0].replace('-','/'),str(previous_period_start).split(' ')[0].replace('-','/'))
    order_items_previous_period = RetailOrderItem.objects.filter(order__day_created__range =[previous_period_start, previous_period_end+relativedelta(days=1)]).order_by('-day_added')
    last_year_start = date_start - relativedelta(years=1)
    last_year_end = date_end - relativedelta(years=1)
    orders_items_last_year = RetailOrderItem.objects.filter(order__day_created__range =[last_year_start,last_year_end]).order_by('-day_added')
    order_items, order_items_previous_period, orders_items_last_year = order_items_filter(request, order_items, order_items_previous_period, orders_items_last_year)
    # analysis
    total_report = [0, 0, 0, 0, 0]  #  incomes, profit, cost, taxes, count
    sells = order_items.filter(order__order_type__in=['r', 'e'])
    returns = order_items.filter(order__order_type='b')
    incomes_total = sells.aggregate(total=Sum(F('price')*F('qty')))['total'] if sells else 0
    return_total = returns.aggregate(total=Sum(F('price')*F('qty')))['total'] if returns else 0
    total_report[0] = incomes_total - return_total

    '''
    ware_cate_report, vendors_report, costumers_report = {}, {}, {}
    for order in order_items:
        if order.order.order_type in ['r','e']:
            total_report[0], total_report[1], total_report[2],total_report[3] = [total_report[0] +order.total_price_number(), total_report[1]+order.total_cost(), total_report[2]+order.total_taxes(),total_report[3]+order.qty]
            if order.title.supplier in vendors_report.keys():
                #splits the information per vendor
                get_data = vendors_report[order.title.supplier]
                get_data[0], get_data[1], get_data[2], get_data[3] = [get_data[0]+order.total_price_number(), get_data[1]+order.total_cost(), get_data[2]+order.total_taxes(), get_data[3]+order.qty]
                vendors_report[order.title.supplier] = get_data
            else:
                vendors_report[order.title.supplier] = [order.total_price_number(), order.total_cost(),order.total_taxes(), order.qty, 0,0,0,0,0,0,0,0]
            if order.title.category in ware_cate_report.keys():
                get_data = ware_cate_report[order.title.category]
                ware_cate_report[order.title.category] = get_data
            else:
                ware_cate_report[order.title.category] = [order.total_price_number(), order.total_cost(),order.total_taxes(), order.qty, 0,0,0,0,0,0,0,0]
            if order.order.costumer_account in costumers_report.keys():
                get_data = costumers_report[order.order.costumer_account]
                get_data[0], get_data[1], get_data[2], get_data[3] = [get_data[0]+order.total_price_number(), get_data[1]+order.total_cost(), get_data[2]+order.total_taxes(), get_data[3]+order.qty]
                costumers_report[order.order.costumer_account] = get_data
            else:
                costumers_report[order.order.costumer_account] = [order.total_price_number(), order.total_cost(),order.total_taxes(), order.qty, 0,0,0,0,0,0,0,0]
    total_previous_period = [0,0,0,0]
    for order in order_items_previous_period:
        if order.order.order_type in ['e','r']:
            total_previous_period[0] += order.total_price_number()
            total_previous_period[1] += order.total_cost()
            total_previous_period[2] += order.total_taxes()
            total_previous_period[3] += order.qty
            if order.title.supplier in vendors_report.keys():
                get_data = vendors_report[order.title.supplier]
                get_data[4], get_data[5], get_data[6], get_data[7] = [get_data[4]+order.total_price_number(), get_data[5]+order.total_cost(), get_data[6]+order.total_taxes(), get_data[7]+order.qty]
                vendors_report[order.title.supplier] = get_data
            else:
                vendors_report[order.title.supplier] = [0,0,0,0,order.total_price_number(), order.total_cost(),order.total_taxes(), order.qty, 0,0,0,0]
            if order.title.category in ware_cate_report.keys():
                get_data = ware_cate_report[order.title.category]
                get_data[4], get_data[5], get_data[6], get_data[7] = [get_data[4]+order.total_price_number(), get_data[5]+order.total_cost(), get_data[6]+order.total_taxes(), get_data[7]+order.qty]
                ware_cate_report[order.title.category] = get_data
            else:
                ware_cate_report[order.title.category] = [0,0,0,0,order.total_price_number(), order.total_cost(),order.total_taxes(), order.qty, 0,0,0,0]
            if order.order.costumer_account in costumers_report.keys():
                get_data = costumers_report[order.order.costumer_account]
                get_data[4], get_data[5], get_data[6], get_data[7] = [get_data[4]+order.total_price_number(), get_data[5]+order.total_cost(), get_data[6]+order.total_taxes(), get_data[7]+order.qty]
                costumers_report[order.order.costumer_account] = get_data
            else:
                costumers_report[order.order.costumer_account] = [0,0,0,0,order.total_price_number(), order.total_cost(),order.total_taxes(), order.qty, 0,0,0,0]
        last_year_total = [0,0,0,0]
        for order in orders_items_last_year:
            last_year_total[0] += order.total_price_number()
            last_year_total[1] += order.total_cost()
            last_year_total[2] += order.total_taxes()
            last_year_total[3] += order.qty
            if order.title.supplier in vendors_report.keys():
                get_data = vendors_report[order.title.supplier]
                get_data[8], get_data[9], get_data[10], get_data[11] = [get_data[8]+order.total_price_number(), get_data[9]+order.total_cost(), get_data[10]+order.total_taxes(), get_data[11]+order.qty]
                vendors_report[order.title.supplier] = get_data
            else:
                vendors_report[order.title.supplier] = [0,0,0,0, 0,0,0,0, order.total_price_number(), order.total_cost(),order.total_taxes(), order.qty, ]
            if order.title.category in ware_cate_report.keys():
                get_data = ware_cate_report[order.title.category]
                get_data[8], get_data[9], get_data[10], get_data[11] = [get_data[8]+order.total_price_number(), get_data[9]+order.total_cost(), get_data[10]+order.total_taxes(), get_data[11]+order.qty]
                ware_cate_report[order.title.category] = get_data
            else:
                ware_cate_report[order.title.category] = [0,0,0,0, 0,0,0,0, order.total_price_number(), order.total_cost(),order.total_taxes(), order.qty, ]
            if order.order.costumer_account in costumers_report.keys():
                get_data = costumers_report[order.order.costumer_account]
                get_data[8], get_data[9], get_data[10], get_data[11] = [get_data[8]+order.total_price_number(), get_data[9]+order.total_cost(), get_data[10]+order.total_taxes(), get_data[11]+order.qty]
                costumers_report[order.order.costumer_account] = get_data
            else:
                costumers_report[order.order.costumer_account] = [0,0,0,0, 0,0,0,0, order.total_price_number(), order.total_cost(),order.total_taxes(), order.qty, ]
    '''
    page = request.GET.get('page')
    paginator = Paginator(order_items, 50)
    try:
        order_items = paginator.page(page)
    except PageNotAnInteger:
        order_items = paginator.page(1)
    except EmptyPage:
        order_items = paginator.page(paginator.num_pages)
    context = locals()
    return render(request, 'reports/order_item_flow.html', context)


class CostumersReport(ListView):
    template_name = 'report/costumers-report.html'
    model = CostumerAccount
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super(CostumersReport, self).get_context_data(**kwargs)

        context.update(locals())
        return context


@staff_member_required
def costumers_accounts_report(request):
    currency = CURRENCY
    title = 'Πελάτες'
    costumer_account = CostumerAccount.objects.all()
    search_text = request.POST.get('search_pro') or None
    if search_text:
        search_text = search_text
        costumer_account = costumer_account.filter(Q(first_name__icontains = search_text)|
                                                   Q(last_name__icontains = search_text)|
                                                   Q(user__email__icontains = search_text)|
                                                   Q(phone__icontains = search_text)|
                                                   Q(cellphone__icontains = search_text)
                                                   ).distinct()
    context = locals()
    context.update(csrf(request))
    return render_to_response('reports/costumer_account_report.html', context)


@staff_member_required
def specific_costumer_account(request, dk):
    costumer_account = CostumerAccount.objects.all()
    costumer_account_spe = CostumerAccount.objects.get(id=dk)
    orders = RetailOrder.objects.filter(costumer_account=costumer_account_spe)
    search_text = request.POST.get('search_pro') or None
    if search_text:
        search_text = search_text
        costumer_account = costumer_account.filter(Q(first_name__icontains = search_text)|
                                                   Q(last_name__icontains = search_text)|
                                                   Q(user__email__icontains = search_text)|
                                                   Q(phone__icontains = search_text)|
                                                   Q(cellphone__icontains = search_text)
                                                   ).distinct()

    context = locals()
    context.update(csrf(request))
    return render_to_response('reports/costumer_account_report.html', context)


class BalanceSheet(TemplateView):
    template_name = 'report/balance-sheet.html'

    def get_context_data(self, **kwargs):
        context = super(BalanceSheet, self).get_context_data(**kwargs)
        date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(self.request)
        date_pick, currency = self.request.GET.get('date_pick'), CURRENCY
        retail_orders = RetailOrder.my_query.all_orders_by_date_filter(date_start, date_end)
        warehouse_orders = Order.objects.filter(day_created__range=[date_start, date_end])
        bills_orders = FixedCostInvoice.objects.filter(date_expired__range=[date_start, date_end])
        payroll_orders = PayrollInvoice.objects.filter(date_expired__range=[date_start, date_end],)
        # expenses
        total_expenses = [round(warehouse_orders.aggregate(Sum('total_price'))['total_price__sum'], 2) if warehouse_orders else 0,
                          round(bills_orders.aggregate(Sum('final_price'))['final_price__sum'], 2) if bills_orders else 0,
                          round(payroll_orders.aggregate(Sum('value'))['value__sum'], 2) if payroll_orders else 0,
                          0]
        total_expenses[3] = total_expenses[0] + total_expenses[1] + total_expenses[2]
        warehouse_orders_by_month = warehouse_orders.annotate(month=TruncMonth('day_created')
                                                              ).values('month').annotate(total_cost=Sum('total_price'),
                                                                                         total_paid=Sum('paid_value')
                                                                                         ).order_by('month')
        bills_orders_by_month = bills_orders.annotate(month=TruncMonth('date_expired')
                                                      ).values('month').annotate(total_cost=Sum('final_price'),
                                                                                 total_paid=Sum('paid_value')
                                                                                 ).order_by('month')
        payroll_orders_by_month = payroll_orders.annotate(month=TruncMonth('date_expired')
                                                          ).values('month').annotate(total_cost=Sum('value'),
                                                                                     total_paid=Sum('paid_value')
                                                                                     ).order_by('month')
        
                                         
        total_expenses_by_month = []
        for ele in warehouse_orders_by_month:
            total_expenses_by_month.append([ele['month'].strftime('%B'), [ele['total_cost'],
                                                           ele['total_paid'],

                                                          ]
                                            ])
        for ele in bills_orders_by_month:
            for data in total_expenses_by_month:
                if ele['month'].strftime('%B') == data[0]:
                    data[1][0] += ele['total_cost']
                    data[1][1] += ele['total_paid']
        for ele in payroll_orders_by_month:
            for data in total_expenses_by_month:
                if ele['month'].strftime('%B') == data[0]:
                    data[1][0] += ele['total_cost']
                    data[1][1] += ele['total_paid']
        # incomes
        retail_orders = RetailOrder.my_query.all_orders_by_date_filter(date_start, date_end)
        incomes, orders_return, orders_destroy = retail_orders.filter(order_type__in=['r', 'e']),\
                                                  retail_orders.filter(order_type='b'), retail_orders.filter(order_type='d')
        total_incomes = [incomes.aggregate(Sum('final_price'))['final_price__sum'] if incomes else 0,
                         orders_return.aggregate(Sum('final_price'))['final_price__sum'] if orders_return else 0,
                         orders_destroy.aggregate(Sum('total_cost'))['total_cost__sum'] if orders_destroy else 0,
                         0]
        total_incomes[3] = total_incomes[0]-total_incomes[1]-total_incomes[2]
        incomes_per_month = incomes.annotate(month=TruncMonth('date_created')
                                             ).values('month').annotate(total_income=Sum('final_price'),
                                                                        total_paid=Sum('paid_value'),
                                                                        total_cost=Sum('total_cost')
                                                                        ).order_by('month')
        orders_return_per_month = orders_return.annotate(month=TruncMonth('date_created')
                                             ).values('month').annotate(total_income=Sum('final_price'),
                                                                        total_paid=Sum('paid_value'),
                                                                        total_cost=Sum('total_cost')
                                                                        ).order_by('month')

        clean_incomes_per_month = []
        for ele in incomes_per_month:
            clean_incomes_per_month.append([ele['month'], [ele['total_income'],
                                                           ele['total_paid'],
                                                           ele['total_paid']
                                                          ]
                                            ])
        for ele in orders_return_per_month:
            for data in clean_incomes_per_month:
                if ele['month'] == data[0]:
                    data[1][0] -= ele['total_income']
                    data[1][1] -= ele['total_paid']
                    data[1][2] -= ele['total_paid']

        profit_losses = []
        for ele in clean_incomes_per_month:
            profit_losses.append([ele[0], ele[1][0]])

        for ele in total_expenses_by_month:
            for data in profit_losses:
                if data[0].strftime('%B') == ele[0]:
                    data[1] -= ele[1][0]
        context.update(locals())
        return context


class PaymentFlow(ListView):
    model = PaymentOrders
    template_name = 'report/payment-flow.html'

    def get_queryset(self):
        start_year, day_now, date_range, months_list = estimate_date_start_end_and_months(self.request)
        queryset = PaymentOrders.objects.filter(date_expired__range=[start_year, day_now])
        search_name, payment_name, is_paid_name, vendor_name, category_name, status_name, date_pick = filters_name(self.request)
        queryset = queryset.filter(payment_type__in=payment_name) if payment_name else queryset
        queryset = queryset.fiter(is_paid=True) if is_paid_name and is_paid_name in [True, False] else queryset
        return queryset

    def get_context_data(self, **kwargs):
        context = super(PaymentFlow, self).get_context_data(**kwargs)
        #  filters
        payment_type, payment_order_type, currency  = PAYMENT_TYPE, PAYMENT_ORDER_TYPE, CURRENCY
        search_name, payment_name, is_paid_name, vendor_name, category_name, status_name, date_pick = filters_name(self.request)
        date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(self.request)
        payment_analysis = self.object_list.values('content_type__model').annotate(total_paid=Sum('value')
                                                                    ).order_by('content_type')
        for ele in payment_analysis:
            print(ele)
        months = diff_month(date_start, date_end)
        orders_outcome = self.object_list.filter(is_expense=True)
        orders_income = self.object_list.filter(is_expense=False)
        orders_income_total = [orders_income.aggregate(Sum('value'))['value__sum'] if orders_income else 0,
                               orders_income.filter(is_paid=True).aggregate(Sum('value'))['value__sum'] if orders_income else 0 
        ]
        orders_outcome_total = [orders_outcome.aggregate(Sum('value'))['value__sum'] if orders_income else 0,
                                orders_outcome.filter(is_paid=True).aggregate(Sum('value'))['value__sum'] if orders_income else 0 
        ]

        # charts
        orders_outcome_chart = balance_sheet_chart_analysis_for_date_expired(date_start, date_end, orders_outcome, 'value')
        orders_income_chart = balance_sheet_chart_analysis_for_date_expired(date_start, date_end, orders_income, 'value')
        diff_chart = [orders_income_chart[i][1] - orders_outcome_chart[i][1] for i in range(months+1)]
        context.update(locals())
        return context





