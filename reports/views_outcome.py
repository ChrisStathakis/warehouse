from django.shortcuts import render, get_object_or_404
from django.db.models import Q, F
from django.views.generic import ListView, DetailView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import  Sum
from django.template.context_processors import csrf
from point_of_sale.models import *
from transcations.models import *
from inventory_manager.payment_models import PayOrders, CHOICES_
from dateutil.relativedelta import relativedelta
from itertools import chain
import datetime
from .tools.outcomes_functions import filters_payroll, filter_payroll_invoice_queryset
from .reports_tools import filters_name, estimate_date_start_end_and_months, balance_sheet_chart_analysis, balance_sheet_chart_analysis_for_date_expired
from .tools.general_fuctions import *
from .tools.outcomes_functions import (outcome_analysis_per_month,
                                       bills_analysis_per_month ,
                                       salary_analysis_per_month,
                                       get_outcomes_filter_data,
                                       outcomes_filter_queryset
                                       )

MONTHS = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']


# ---------------------------------Outcomes section--------------------------------------------

@staff_member_required
def outcome(request):
    currency = CURRENCY
    year_start, day_now, date_range, months_list = estimate_date_start_end_and_months(request)
    months = diff_month(year_start, day_now)
    search_name, payment_name, is_paid_name, vendor_name, category_name, status_name, date_pick = filters_name(
        request)
    warehouse_orders = Order.objects.filter(date_created__range=[year_start, day_now])
    bills = FixedCostInvoice.objects.filter(date_expired__range=[year_start, day_now])
    salary = PayrollInvoice.objects.filter(date_expired__range=[year_start, day_now])

    warehouse_orders_total = warehouse_orders.aggregate(Sum('total_price'))['total_price__sum'] if warehouse_orders else 0
    warehouse_orders_paid = warehouse_orders.aggregate(Sum('paid_value'))['paid_value__sum'] if warehouse_orders else 0
    bills_total = bills.aggregate(Sum('final_price'))['final_price__sum'] if bills else 0
    bills_paid = bills.aggregate(Sum('paid_value'))['paid_value__sum'] if bills else 0
    salary_total = salary.aggregate(Sum('value'))['value__sum'] if salary else 0
    salary_paid = salary.aggregate(Sum('paid_value'))['paid_value__sum'] if salary else 0
    #  chart data
    warehouse_orders_total_chart = balance_sheet_chart_analysis(year_start, day_now, warehouse_orders, 'total_price')
    bills_total_chart = balance_sheet_chart_analysis_for_date_expired(year_start, day_now, bills, 'final_price')
    salary_total_chart = balance_sheet_chart_analysis_for_date_expired(year_start, day_now, salary, 'paid_value')
    total_chart = [warehouse_orders_total_chart[i][1] + bills_total_chart[i][1] + salary_total_chart[i][1] for i in range(months+1)]

    warehouse_orders_pending = Order.my_query.pending_orders()[:10]
    bills_orders_pending = FixedCostInvoice.objects.filter(is_paid=False)[:10]
    salary_pending = PayrollInvoice.objects.filter(is_paid=False)[:10]
    context = locals()
    return render(request, 'report/outcome.html', context)


@staff_member_required
def payment_analysis(request):
    currency = CURRENCY
    date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(request)
    months = diff_month(date_start, date_end)
    search_name, payment_name, is_paid_name, vendor_name, category_name, status_name, date_pick = filters_name(
        request)
    # filters
    vendors, payment_method, bills_accounts, occupation_accounts = Supply.objects.all(), \
        PAYMENT_TYPE, FixedCostsItem.objects.all(), Occupation.objects.all(),

    payment_orders = PaymentOrders.objects.filter(date_expired__range=[date_start, date_end], is_expense=True)
    payment_total = payment_orders.aggregate(Sum('value'))['value__sum'] if payment_orders.exists() else 0
    payment_paid = payment_orders.filter(is_paid=True).aggregate(Sum('value'))['value__sum'] if payment_orders.filter(is_paid=True).exists() else 0
    # totals
    ware_orders_payments = payment_orders.filter(content_type__model='order')
    bills_payments = payment_orders.filter(content_type__model='fixedcostinvoice')
    salary_paid = payment_orders.filter(content_type__model='payrollinvoice')
    orders_total = ware_orders_payments.aggregate(Sum('value'))['value__sum'] if ware_orders_payments else 0
    bills_total = bills_payments.aggregate(Sum('value'))['value__sum'] if bills_payments else 0
    salary_total = salary_paid.aggregate(Sum('value'))['value__sum'] if salary_paid else 0

    context = locals()
    return render(request, 'report/payment_analysis.html', context)


class WarehouseOrdersReport(ListView):
    model = Order
    template_name = 'report/orders.html'

    def get_queryset(self):
        date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(self.request)
        search_name, payment_name, is_paid_name, vendor_name, category_name, status_name, date_pick = filters_name(
            self.request)
        queryset = Order.objects.filter(day_created__range=[date_start, date_end])
        queryset = queryset.filter(vendor__id__in=vendor_name) if vendor_name else queryset
        queryset = queryset.filter(payment_method__in=payment_name) if payment_name else queryset
        queryset = queryset.filter(is_paid=True) if is_paid_name == 'a' else queryset
        queryset = queryset.filter(is_paid=False) if is_paid_name == 'b' else  queryset
        queryset = queryset.filter(Q(code__icontains=search_name) |
                                   Q(vendor__title__icontains=search_name)
                                   ).distinct() if search_name else queryset
        return queryset

    def get_context_data(self, **kwargs):
        context = super(WarehouseOrdersReport, self).get_context_data(**kwargs)
        date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(self.request)
        #  filters
        search_name, payment_name, is_paid_name, vendor_name, category_name, status_name, date_pick = filters_name(
            self.request)
        print(date_pick)
        vendors = Supply.objects.all()
        payment_method = PAYMENT_TYPE
        currency = CURRENCY
        order_count, total_value, paid_value = self.object_list.count(), self.object_list.aggregate(Sum('total_price'))['total_price__sum']\
            if self.object_list else 0, self.object_list.aggregate(Sum('paid_value'))['paid_value__sum'] if self.object_list else 0
        diff = total_value - paid_value
        warehouse_analysis = balance_sheet_chart_analysis(date_start, date_end, self.object_list, 'total_price')
        warehouse_vendors = self.object_list.values('vendor__title').annotate(value_total=Sum('total_price'), paid_val=Sum('paid_value')).order_by('-value_total')
        context.update(locals())
        return context


class WarehouseOrderDetail(DetailView):
    model = Order
    template_name = 'report/details/warehouse-order-detail.html'

    def get_context_data(self, **kwargs):
        context = super(WarehouseOrderDetail, self).get_context_data(**kwargs)

        context.update(locals())
        return context


class BillsAndAssetsPage(ListView):
    model = FixedCostInvoice
    template_name = 'report/outcome-bills.html'

    def get_queryset(self):
        date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(self.request)
        queryset = FixedCostInvoice.objects.filter(date_expired__range=[date_start, date_end])
        queryset = outcomes_filter_queryset(self.request, queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(BillsAndAssetsPage, self).get_context_data(**kwargs)
        currency = CURRENCY
        #  filters
        bills_name, bills_group_name, search_name, paid_name = get_outcomes_filter_data(self.request)
        bills = FixedCostsItem.objects.all()
        bills_group = FixedCosts.objects.all()

        #  reports
        total_value = self.object_list.aggregate(Sum('final_price'))['final_price__sum'] if self.object_list else 0
        paid_value = self.object_list.aggregate(Sum('paid_value'))['paid_value__sum'] if self.object_list else 0
        diff = total_value - paid_value
        value_per_bill = self.object_list.values('category__title').annotate(val=Sum('final_price')).order_by('category__title')
        paid_per_bill = self.object_list.values('category__title').annotate(val=Sum('paid_value')).order_by('category__title')
        for val in value_per_bill:
            print(val)
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class PayrollPage(ListView):
    model = PayrollInvoice
    template_name = 'report/outcome-payments.html'
    paginate_by = 50

    def get_queryset(self):
        date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(self.request)
        queryset = PayrollInvoice.objects.filter(date_expired__range=[date_start, date_end])
        queryset = filter_payroll_invoice_queryset(self.request, queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(PayrollPage, self).get_context_data(**kwargs)
        currency = CURRENCY
        date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(self.request)
        months = diff_month(date_start, date_end)
        #  filters
        occupations = Occupation.objects.all()
        persons = Person.objects.all()
        stores = Store.objects.all()
        categories = PAYROLL_CHOICES
        search_name, payment_name, is_paid_name, occup_name, person_name, store_name, cate_name = filters_payroll(
            self.request)
        # totals
        total_value = self.object_list.aggregate(Sum('value'))['value__sum'] if self.object_list.exists() else 0
        paid_value = self.object_list.aggregate(Sum('paid_value'))['paid_value__sum'] if self.object_list.exists() else 0
        diff = total_value - paid_value
        #  charts
        warehouse_analysis = balance_sheet_chart_analysis_for_date_expired(date_start, date_end, self.object_list, 'value')
        analysis_per_person = self.object_list.values('person__title').annotate(remai=Sum('value')).order_by('-remai')
        analysis_per_cate = self.object_list.values('category').annotate(occup_value=Sum('value')).order_by('-occup_value')
        choices = PAYROLL_CHOICES
        '''
        for entry in analysis_per_cate:
            print(entry['category'])
            new_choice = choices[int(entry['category'])-1][1]
            entry['category'] = new_choice
        '''
        context.update(locals())
        return context


class PersonPayrollReport(ListView):
    model = PayrollInvoice
    template_name = 'report/details/payroll_person.html'

    def get_queryset(self):
        instance = get_object_or_404(Person, id=self.kwargs['dk'])
        queryset = PayrollInvoice.my_query.invoice_per_person(instance=instance)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(PersonPayrollReport, self).get_context_data(**kwargs)
        person = get_object_or_404(Person, id=self.kwargs['dk'])
        payment_orders = ContentType.objects.get_for_model(PaymentOrders)

        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class PayrollInvoiceDetail(DetailView):
    model = PayrollInvoice
    template_name = ''

    def get_context_data(self, **kwargs):
        context = super(PayrollInvoiceDetail, self).get_context_data(**kwargs)

        context.update(locals())
        return context