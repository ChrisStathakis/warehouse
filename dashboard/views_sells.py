from django.shortcuts import render, redirect, HttpResponseRedirect, reverse, get_object_or_404
from django.views.generic import ListView, DetailView, View, CreateView, FormView, TemplateView
from django.db.models import Q, Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from account.models import ExtendsUser
from products.models import *
from products.forms import *
from cart.models import Cart, Coupons
from cart.forms import CouponForm
from point_of_sale.models import *
from point_of_sale.forms import EshopRetailForm, EshopOrderItemForm
from transcations.models import *
from .tools_views import grab_orders_filter_data, orders_filtering


class EshopOrdersPage(ListView):
    model = RetailOrder
    template_name = 'dashboard/order_section/order_list.html'
    paginate_by = 20

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(EshopOrdersPage, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        queryset = RetailOrder.objects.filter(order_type='e')
        queryset = orders_filtering(self.request, queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(EshopOrdersPage, self).get_context_data(**kwargs)
        status_list, payment_method_list = ORDER_STATUS, PAYMENT_TYPE
        not_paid_name, paid_name, not_printed_name, status_name, payment_name = grab_orders_filter_data(self.request)
        context.update(locals())
        return context


class CartListPage(ListView):
    model = Cart
    template_name = 'dashboard/order_section/cart_page.html'
    paginate_by = 30


class OrderSettingsPage(TemplateView):
    template_name = 'dashboard/order_section/settings_page.html'

    def get_context_data(self, **kwargs):
        context = super(OrderSettingsPage, self).get_context_data(**kwargs)
        shipping_methods = Shipping.objects.all()
        coupons = Coupons.objects.all()
        context.update(locals())
        return context


class CouponEditPage(FormView):
    model = Coupons
    template_name = ''
    form_class = CouponForm


@login_required()
def create_eshop_order(request):
    new_order = RetailOrder.objects.create(order_type='e',
                                           seller_account=request.user,
                                           )
    new_order.refresh_from_db()
    return HttpResponseRedirect(reverse('dashboard:eshop_order_edit',
                                        args=(new_order.id,)))


@staff_member_required()
def eshop_order_edit(request, pk):
    object = get_object_or_404(RetailOrder, id=pk)
    object_list = Product.my_query.active_for_site()
    order_items = RetailOrderItem.objects.filter(order=object)
    form = EshopRetailForm(request.POST or None, instance=object)

    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('dashboard:eshop_order_edit',
                                            args=(object.id,)))

    search_name = request.GET.get('search_name', None)
    object_list = object_list.filter(title__icontains=search_name) if search_name else object_list
    paninator = Paginator(object_list, 50)
    object_list = paninator.get_page(1)
    return render(request, 'dashboard/order_section/order_create.html', context=locals())


@login_required()
def add_edit_order_item(request, dk, pk, qty):
    order = get_object_or_404(RetailOrder, id=dk)
    product = get_object_or_404(Product, id=pk)
    exists = RetailOrderItem.objects.filter(title=product, order=order)
    if exists.exists():
        new_order_item = exists.last()
        new_order_item.qty += qty
        new_order_item.save()
    else:
        new_order_item = RetailOrderItem.objects.create(title= product,
                                                        order=order,
                                                        cost=product.price_buy,
                                                        price=product.price,
                                                        qty=qty,
                                                        discount=product.price_discount,
                                                        )
    return HttpResponseRedirect(reverse('dashboard:eshop_order_edit', args=(dk,)))


@login_required()
def edit_order_item(request, dk):
    instance = get_object_or_404(RetailOrderItem, id=dk)
    form_order = EshopOrderItemForm(request.POST or None, instance=instance)
    if form_order.is_valid():
        form_order.save()
        return HttpResponseRedirect(reverse('dashboard:eshop_order_edit', args=(instance.order.id,)))
    context = locals()
    return render(request, 'dashboard/order_section/edit_order_item.html', context)


@login_required()
def delete_order_item(request, dk):
    instance = get_object_or_404(RetailOrderItem, id=dk)
    order = instance.order
    instance.delete()
    return HttpResponseRedirect(reverse('dashboard:eshop_order_edit', args=(order.id,)))