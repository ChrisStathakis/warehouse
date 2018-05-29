from django.shortcuts import render, render_to_response, HttpResponseRedirect, redirect, get_object_or_404, get_list_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib import messages
from django.db.models import Q, F
from django.utils.decorators import method_decorator
#from django.db.models.functions import TruncMonth
from django.db.models import ExpressionWrapper, DecimalField
from django.template.context_processors import csrf
from django.contrib.admin.views.decorators import staff_member_required

from account.models import CostumerAccount
from itertools import chain
from operator import attrgetter
from dateutil.relativedelta import relativedelta
import datetime

from .reports_tools import *
from .tools.warehouse_functions import (warehouse_get_filters_data,
                                        warehouse_filters_data, 
                                        warehouse_filters
                                        )
from products.utils import *
from products.models import *
from inventory_manager.models import *
from inventory_manager.payment_models import *
from point_of_sale.models import *

from transcations.models import *


MONTHS = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

# Create your views here.


def get_month_sales(query, return_query, value, return_value):
    sells = query.aggregate(Sum(value))['%s__sum' % value] if query.aggregate(Sum(value))['%s__sum' % value]  else 0
    returns = return_query.aggregate(Sum(return_value))['%s__sum' % return_value] if return_query.aggregate(Sum(return_value))['%s__sum' % return_value] else 0
    return sells - returns


@staff_member_required
def homepage(request):
    title = 'Αρχική σελίδα Αποθήκης'
    today = datetime.datetime.now()
    start_of_month = '%s-%s-1' % (today.year, today.month)
    incomes = RetailOrder.objects.filter(date_created__range=[start_of_month, today])
    retail_incomes, eshop_incomes, return_incomes = incomes.filter(order_type='r'), incomes.filter(order_type='e'), incomes.filter(order_type='b')
    total_incomes = get_month_sales(incomes, return_incomes, 'paid_value', 'value')
    retail_incomes = get_month_sales(retail_incomes, return_incomes, 'paid_value', 'value')
    eshop_incomes = get_month_sales(eshop_incomes, return_incomes, 'paid_value', 'value')
    wholesale_incomes = 0
    destroy_value = 0
    #  orders warehouse
    orders = Order.objects.filter(day_created__range=[start_of_month, today])
    orders_total_value = orders.aggregate(Sum('total_price'))['total_price__sum'] if orders.aggregate(Sum('total_price'))['total_price__sum'] else 0
    orders_clear_value = orders.aggregate(Sum('total_price_after_discount'))['total_price_after_discount__sum'] if orders.aggregate(Sum('total_price_after_discount'))['total_price_after_discount__sum'] else 0
    orders_taxes_value = orders.aggregate(Sum('total_taxes'))['total_taxes__sum'] if orders.aggregate(Sum('total_taxes'))['total_taxes__sum'] else 0
    orders_paid = orders.filter(is_paid=True).aggregate(Sum('total_price'))['total_price__sum'] if orders.filter(is_paid=True).aggregate(Sum('total_price'))['total_price__sum'] else 0
    orders_remaining_paid = orders_total_value - orders_paid
    #  bills
    bills = FixedCostsItem.objects.filter(category__id=1)
    #  misthodosia
    payroll = Occupation.objects.all()
    context = locals()
    return render(request,'report/warehouse.html', context)


@method_decorator(staff_member_required, name='dispatch')
class ReportProducts(ListView):
    template_name = 'report/products.html'
    model = Product
    paginate_by = 100

    def get_queryset(self):
        queryset = Product.my_query.active_warehouse()
        queryset = Product.filters_data(self.request, queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ReportProducts, self).get_context_data(**kwargs)
        currency = CURRENCY
        # filters
        products, category_name, vendor_name, color_name, discount_name, qty_name = warehouse_filters(self.request, self.object_list)
        vendors, categories, categories_site, colors, sizes, brands = initial_data_from_database()
        search_name = self.request.GET.get('search_name', None)
        print(search_name)
        products_count = self.object_list.aggregate(Sum('qty'))['qty__sum'] if self.object_list else 0
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class ProductDetail(LoginRequiredMixin, DetailView):
    template_name = 'report/details/products_id.html'
    model = Product

    def get_context_data(self, **kwargs):
        context = super(ProductDetail, self).get_context_data(**kwargs)
        date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(self.request)
        date_pick, currency = self.request.GET.get('date_pick'), CURRENCY
        date_end = date_end + relativedelta(days=1)
        order_items = OrderItem.objects.filter(product=self.object,
                                               order__day_created__range=[date_start, date_end]
                                               )
        order_items_analysis = order_items.values('product').annotate(total_clean=Sum('total_clean_value'),
                                                                      total_tax=Sum('total_value_with_taxes'),
                                                                      qty_count=Sum('qty'),
                                                                      )
        # retail orders
        retail_items = RetailOrderItem.objects.filter(title=self.object,
                                                      day_added__range=[date_start, date_end]
                                                      )
        retail_sells_by_type = retail_items.values('order__order_type').annotate(total_incomes=Sum(F('qty')*F('final_price')),
                                                                                 total_qty=Sum('qty'),
                                                                                 ).order_by('order__order_type')

        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class Vendors(ListView):
    model = Vendor
    template_name = 'report/vendors.html'
    paginate_by = 50

    def get_queryset(self):
        queryset = Supply.objects.all()
        queryset = Supply.filter_data(self.request, queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(Vendors, self).get_context_data(**kwargs)
        vendors = Supply.objects.all()
        date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(self.request)
        date_start_last_year, date_end_last_year = date_start- relativedelta(year=1), date_end-relativedelta(year=1)
        date_pick, currency = self.request.GET.get('date_pick'), CURRENCY
        vendor_name, balance_name, search_name =[self.request.GET.getlist('vendor_name'),
                                                 self.request.GET.get('balance_name'),
                                                 self.request.GET.get('search_name'),
                                                ]

        orders = Order.objects.filter(date_created__range=[date_start, date_end])
        chart_data = [Supply.objects.all().aggregate(Sum('balance'))['balance__sum'] if Supply.objects.all() else 0,
                      orders.aggregate(Sum('total_price'))['total_price__sum'] if orders else 0,
                      orders.aggregate(Sum('paid_value'))['paid_value__sum'] if orders else 0
                  ]
        analysis = warehouse_vendors_analysis(self.request, date_start, date_end)
        analysis_last_year = warehouse_vendors_analysis(self.request, date_start_last_year, date_end_last_year)
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class CheckOrderPage(ListView):
    template_name = 'report/check_orders.html'
    model = PaymentOrders
    paginate_by = 30

    def get_queryset(self):
        queryset = PaymentOrders.objects.all()

        return queryset

    def get_context_data(self, **kwargs):
        context = super(CheckOrderPage, self).get_context_data(**kwargs)
        vendors = Supply.objects.filter(active=True)
        context.update(locals())
        return context


@staff_member_required
def vendor_detail(request, pk):
    instance = get_object_or_404(Supply, id=pk)
    # filters_data
    date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(request)
    vendors, categories, categories_site, colors, sizes, brands = initial_data_from_database()
    date_pick = request.GET.get('date_pick', None)

    # data
    products = Product.my_query.active_warehouse().filter(supply=instance)[:20]
    warehouse_orders = Order.objects.filter(vendor=instance, date_created__range=[date_start, date_end])[:20]
    
    paychecks = list(chain(instance.payment_orders.all().filter(date_expired__range=[date_start, date_end]),
                           PaymentOrders.objects.filter(content_type=ContentType.objects.get_for_model(Order),
                                                        object_id__in=warehouse_orders.values('id'),
                                                        ) 
                          )
                    )[:20]
    order_item_sells = RetailOrderItem.objects.filter(title__in=products, order__date_created__range=[date_start, date_end])[:20]
    context = locals()
    return render(request, 'report/details/vendors_id.html', context)


@staff_member_required
def warehouse_category_reports(request):
    categories, currency = Category.objects.all(), CURRENCY
    site_categories = CategorySite.objects.all()
    context = locals()
    return render(request, 'report/category_report.html', context)


class WarehouseCategoryReport(DetailView):
    model = Category
    template_name = ''



@staff_member_required
def warehouse_orders(request):
    vendors, payment_method, currency = Supply.objects.all(), PaymentMethod.objects.all(), CURRENCY
    orders = Order.objects.all()
    orders = Order.filter_data(request, queryset=orders)

    date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(request)
    search_name, vendor_name, balance_name, paid_name = [request.GET.get('search_name'),
                                                         request.GET.getlist('vendor_name'),
                                                         request.GET.get('balance_name'),
                                                         request.GET.get('paid_name')
                                                         ]

    order_count, total_value, paid_value = orders.count(), orders.aggregate(Sum('total_price'))[
        'total_price__sum'] \
        if orders else 0, orders.aggregate(Sum('paid_value'))[
                                               'paid_value__sum'] if orders else 0
    diff = total_value - paid_value
    warehouse_analysis = balance_sheet_chart_analysis(date_start, date_end, orders, 'total_price')
    warehouse_vendors = orders.values('vendor__title').annotate(value_total=Sum('total_price'),
                                                                          paid_val=Sum('paid_value')).order_by(
        '-value_total')
    paginator = Paginator(orders, 100)
    page = request.GET.get('page', 1)
    orders = paginator.get_page(page)
    context = locals()
    return render(request, 'report/orders.html', context)


@staff_member_required
def order_id(request, dk):
    currency = CURRENCY
    order = get_object_or_404(Order, id=dk)
    order_items = order.orderitem_set.all()
    orders_files = order.warehouseorderimage_set.all()
    payments_orders = order.payment_orders
    context = locals()
    return render(request, 'report/details/orders_id.html', context)


@staff_member_required
def warehouse_order_items_movements(request):
    vendors, categories, categories_site, colors, sizes,  = initial_data_from_database()
    date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(request)
    search_name, payment_name, is_paid_name, vendor_name, category_name, status_name, date_pick = filters_name(
        request)
    warehouse_order_items = get_filters_warehouse_order_items(request, OrderItem.objects.filter(
        order__day_created__range=[date_start, date_end]))
    currency = CURRENCY
    order_items_qty = warehouse_order_items.aggregate(Sum('qty'))['qty__sum'] if warehouse_order_items else 0
    order_items_total_value = warehouse_order_items.aggregate(total=Sum(F('total_clean_value')*F('qty')))['total'] if warehouse_order_items else 0
    avg_total_price = order_items_total_value/order_items_qty if order_items_qty > 0 else 0

    paginator = Paginator(warehouse_order_items, 100)
    page = request.GET.get('page')
    try:
        warehouse_order_items = paginator.page(page)
    except PageNotAnInteger:
        warehouse_order_items = paginator.page(1)
    except EmptyPage:
        warehouse_order_items = paginator.page(paginator.num_pages)
    context = locals()
    return render(request, 'report/warehouse_order_items_movements.html', context)


@staff_member_required
def products_movements(request):
    currency, table = CURRENCY, ToolsTableOrder.objects.get(title='reports_table_product_order')
    date_start, date_end, date_string = reports_initial_date(request)
    check_date = date_pick_session(request)
    if check_date:
        date_start, date_end, date_string = check_date
    vendors, warehouse_cate, colors, sizes = [Supply.objects.all(), Category.objects.all(), Color.objects.all(), Size.objects.all()]
    try:
        products_, sellings, buyings, returns, product_movements, filters_name = warehouse_movements_filters(request, date_start, date_end)
        # category_name, vendor_name, color_name , size_name, query, date_pick
        products, vendors_stats, warehouse_cate_stats, color_stats, size_stats, data_per_point = product_movenent_analysis(products_,
            date_start, date_end, sellings, buyings, returns)
        data_per_point.reverse()
        paginator = Paginator(tuple(products.items()), 50)
        page = request.GET.get('page')
        try:
            contacts = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            contacts = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            contacts = paginator.page(paginator.num_pages)
        page_ = request.GET.get('page_')
        paginator_ = Paginator(product_movements, 30)
        try:
            product_movements = paginator_.page(page_)
        except PageNotAnInteger:
            product_movements = paginator_.page(1)
        except EmptyPage:
            product_movements = paginator_.page(paginator_.num_pages)
    except:
        products, product_movements, filters_name = None, None, None
    context = locals()
    return render(request, 'reports/products_flow.html', context)


@method_decorator(staff_member_required, name='dispatch')
class WarehouseCategoryView(ListView):
    model = Category
    template_name = 'report/category_report.html'
    paginate_by = 50



@staff_member_required
def category_report(request):
    categories, category_site, categories_info, categories_site_info = Category.objects.all(), CategorySite.objects.all(), {}, {}
    # get initial date from now and three months before.
    date_start, date_end, date_string = reports_initial_date(request)
    initial_order_item_buy = OrderItem.objects.filter(order__day_created__range=[date_start, date_end])
    initial_order_item_sell = RetailOrderItem.my_query.selling_order_items(date_start=date_start, date_end=date_end)
    initial_order_item_return = RetailOrderItem.my_query.return_order_items(date_start, date_end)
    #initial_order_item_sell = RetailOrderItem.objects.filter(order__day_created__range=[date_start, date_end])
    for cat in categories:
        qs_buy = initial_order_item_buy.filter(product__category__id=cat.id)
        qs_sell = initial_order_item_sell.filter(title__category=cat)
        qs_return = initial_order_item_return.filter(title__category__id=cat.id)
        categories_info[cat] = [qs_buy.aggregate(Sum('qty'))['qty__sum'] if qs_buy.aggregate(Sum('qty')) else 0,
                                qs_buy.aggregate(total=Sum(F('qty')*F('price')))['total'] if qs_buy.aggregate(total=Sum(F('qty')*F('price')))['total'] else 0,
                                qs_sell.aggregate(Sum('qty'))['qty__sum'] if qs_sell.aggregate(Sum('qty')) else 0,
                                qs_sell.aggregate(total=Sum(F('qty')*F('price')))['total'] if qs_sell.aggregate(total=Sum(F('qty')*F('price')))['total'] else 0,
                                ]
    for cat in category_site:
        categories_site_info[cat] = [qs_buy.aggregate(Sum('qty'))['qty__sum'] if qs_buy.aggregate(Sum('qty')) else 0,
                                qs_buy.aggregate(total=Sum(F('qty') * F('price')))['total'] if
                                qs_buy.aggregate(total=Sum(F('qty') * F('price')))['total'] else 0,
                                qs_sell.aggregate(Sum('qty'))['qty__sum'] if qs_sell.aggregate(Sum('qty')) else 0,
                                qs_sell.aggregate(total=Sum(F('qty') * F('price')))['total'] if
                                qs_sell.aggregate(total=Sum(F('qty') * F('price')))['total'] else 0,
                                ]
    context = locals()
    return render(request, 'reports/category_report.html', context)



@staff_member_required
def add_to_pre_order(request,dk,pk):
    product = Product.objects.get(id=dk)
    try:
        order = PreOrder.objects.filter(status='a').last()
        if request.POST:
            form = PreOrderItemForm(request.POST,initial={'title':product,
                                                          'order':order,})
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/reports/vendors/%s'%(pk))
        else:
            form =PreOrderItemForm(initial={'title':product,
                                            'order':order,})
        context={
            'form':form,
            'title':'Προσθήκη στην Προπαραγγελία.',
            'return_page':'/reports/vendors/%s'%(pk),
        }
        context.update(csrf(request))
        return render(request, 'inventory/create_costumer_form.html', context)
    except:
        messages.warning(request,'Δημιουργήστε Προπαραγγελία πρώτα.')
        return HttpResponseRedirect('/reports/vendors/%s'%(pk))



@staff_member_required
def reports_order_reset_payments(request, dk):
    order = Order.objects.get(id=dk)
    pay_orders = order.payorders_set.all()
    for pay_order in pay_orders:
        pay_order.delete_pay()
        pay_order.delete()
    pay_orders_deposit = order.vendordepositorderpay_set.all()
    for pay_order in pay_orders_deposit:
        pay_order.delete_deposit()
        pay_order.delete()
    order.credit_balance = 0
    order.status = 'p'
    order.save()
    return redirect('order_edit_main', dk=dk)
