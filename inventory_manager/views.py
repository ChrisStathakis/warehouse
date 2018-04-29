from django.shortcuts import render, HttpResponseRedirect, redirect, reverse, get_object_or_404
from django.views.generic import ListView, DetailView, UpdateView, FormView, CreateView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import EmptyPage, Paginator, PageNotAnInteger

from products.models import Supply, Category, Color, Size
from products.forms import VendorForm
from .models import Order
from dashboard.models import PaymentOrders
from dashboard.forms import PaymentForm

import datetime


@method_decorator(staff_member_required, name='dispatch')
class VendorPageList(ListView):
    template_name = 'inventory_manager/vendor_list.html'
    model = Supply
    paginate_by = 10

    def get_queryset(self):
        queryset = Supply.objects.all()
        search_name = self.request.GET.get('search_name', None)
        balance_name = self.request.GET.get('balance_name', None)
        queryset = self.model.filter_data(queryset, search_name, balance_name)

        return queryset

    def get_context_data(self, **kwargs):
        context = super(VendorPageList, self).get_context_data(**kwargs)
        search_name = self.request.GET.get('search_name', None)
        balance_name = self.request.GET.get('balance_name', None)
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class VendorPageDetail(UpdateView):
    template_name = 'inventory_manager/vendor_detail.html'
    form_class = VendorForm
    model = Supply
    
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('inventory:vendor_list')


@method_decorator(staff_member_required, name='dispatch')
class VendorPageCreate(FormView):
    template_name = 'dash_ware/form.html'
    form_class = VendorForm

    def get_context_data(self, **kwargs):
        context = super(VendorPageCreate, self).get_context_data(**kwargs)
        page_title, back_url = 'Create Vendor', reverse('inventory:vendor_create')
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'New Vendor Added!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('inventory:vendor_list')


@method_decorator(staff_member_required, name='dispatch')
class WarehousePaymentPage(ListView):
    model = Order
    template_name = 'inventory_manager/payment_list.html'

    def get_queryset(self):
        queryset = Order.objects.all()
        search_name = self.request.GET.get('search_name', None)
        paid_name = self.request.GET.get('paid_name', None)
        vendor_name = self.request.GET.getlist('vendor_name', None)
        date_start = self.request.GET.get('date_start', None)
        date_end = self.request.GET.get('date_end', None)
        queryset = self.model.filter_data(queryset, search_name, vendor_name, date_start, date_end, paid_name)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(WarehousePaymentPage, self).get_context_data(**kwargs)
        search_name = self.request.GET.get('search_name', None)
        paid_name = self.request.GET.get('paid_name', None)
        vendor_name = self.request.GET.getlist('vendor_name', None)
        date_start = self.request.GET.get('date_start', None)
        date_end = self.request.GET.get('date_end', None)
        vendors  = Supply.objects.filter(active=True)
        context.update(locals())
        return context


@staff_member_required
def warehouse_order_paid(request, pk):
    instance = get_object_or_404(Order, id=pk)
    instance.is_paid = True
    instance.save()
    messages.success(request, 'The order %s is paid.')
    return HttpResponseRedirect(reverse('inventory:payment_list'))


@staff_member_required
def warehouser_order_paid_detail(request, pk):
    instance = get_object_or_404(Order, id=pk)
    vendor = instance.vendor
    create = True
    form = PaymentForm(request.POST or None, initial={'value': instance.get_remaining_value,
                                                      'content_type': ContentType.objects.get_for_model(instance),
                                                      'payment_type': instance.payment_method,
                                                      'title': '%s' % instance.code,
                                                      'date_expired': instance.date_created,
                                                      'object_id': pk,
                                                      'is_expense': True,
                                                      'is_paid':True,
                                                      })
    if request.POST:
        if form.is_valid():
            form.save()
            messages.success(request, 'The payment added!')
            return HttpResponseRedirect(reverse('inventory:ware_order_paid_detail', kwargs={'pk': pk}))
    context = locals()
    return render(request, 'inventory_manager/payment_details.html', context)


@staff_member_required
def warehouse_check_order_convert(request, dk, pk):
    instance = get_object_or_404(PaymentOrders, id=pk)
    order = get_object_or_404(Order, id=dk)
    if instance.value <= order.total_price:
        instance.object_id = dk
        instance.content_type = ContentType.objects.get_for_model(order)
        instance.is_paid = True
        instance.save()
    else:
        new_payment_order = PaymentOrders.objects.create(content_type=ContentType.objects.get_for_model(order),
                                                         object_id=dk,
                                                         title='%s' % order.code,
                                                         date_expired=instance.date_expired,
                                                         payment_type=instance.payment_type,
                                                         bank=instance.bank,
                                                         value=order.total_price,
                                                         is_expense=True,
                                                         is_paid=True
                                                         )
        instance.value -= order.total_price
        instance.save()
    messages.success(request, 'The check order is converted')
    return HttpResponseRedirect(reverse('inventory:ware_order_paid_detail', kwargs={'pk': dk}))
 

@staff_member_required
def warehouse_order_paid_delete(request, pk):
    instance = get_object_or_404(PaymentOrders, id=pk)
    instance.delete()
    messages.warning(request, 'The payment deleted!')
    return HttpResponseRedirect(reverse('inventory:ware_order_paid_detail', kwargs={'pk': instance.object_id}))


@staff_member_required
def warehouse_edit_paid_order(request, dk, pk):
    instance = get_object_or_404(Order, id=dk)
    payorder = get_object_or_404(PaymentOrders, id=pk)
    form = PaymentForm(request.POST or None,
                       instance=payorder,
                       initial={'is_expense': True
                                })
    create = False
    if request.POST:
        if form.is_valid():
            form.save()
            messages.success(request, 'The paid order is edited')
            return HttpResponseRedirect(reverse('inventory:ware_order_paid_detail',
                                                kwargs={'pk': instance.id}
                                                )
                                        )
    context = locals()
    return render(request, 'inventory_manager/form_edit_payment_order.html', context)


@method_decorator(staff_member_required, name='dispatch')
class WarehousePaymentOrderCreate(CreateView):
    template_name = 'dash_ware/form.html'
    model = PaymentOrders
    form_class = PaymentForm

    def get_initial(self):
        initial = super(WarehousePaymentOrderCreate, self).get_initial()
        instance = get_object_or_404(Supply, id=self.kwargs['pk'])
        initial['object_id'] = instance.id
        initial['content_type'] = ContentType.objects.get_for_model(instance)
        initial['date_expired'] = datetime.datetime.now()
        initial['title'] = '%s' % instance.title
        initial['is_expense'] = True
        return initial

    def get_context_data(self, **kwargs):
        context = super(WarehousePaymentOrderCreate, self).get_context_data(**kwargs)
        title = 'Create Check'
        back_url = ''
        context.update(locals())
        return context

    def form_valid(self, form):
        if form.is_valid():
            print('works!')
            form.save()
            messages.success(self.request, 'The check created!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('inventory:vendor_list')


@staff_member_required
def edit_check_order(request, pk):
    instance = get_object_or_404(PaymentOrders, id=pk)
    form = PaymentForm(request.POST or None, instance=instance, initial={'is_expense': True})
    if form.is_valid():
        form.save()
        messages.success(request, 'The Check order is edited')
        return HttpResponseRedirect(reverse('inventory:vendor_detail', kwargs={'pk': instance.object_id }))
    print(form.errors)
    page_title = 'Edit %s' % instance.title
    context = locals()
    return render(request, 'dash_ware/form.html', context)


    def get_success_url(self):
        instance = get_object_or_404(PaymentOrders, id=self.kwargs['pk'])
        return reverse('inventory:vendor_detail', kwargs={'pk': instance.object_id })


@staff_member_required
def delete_check_order(request, pk):
    instance = get_object_or_404(PaymentOrders, id=pk)
    instance.delete()
    messages.warning(request, 'The Payment Order deleted!')
    return HttpResponseRedirect(reverse('inventory:vendor_detail', kwargs={'pk': instance.object_id}))


@staff_member_required
def check_order_paid(request, pk):
    instance = get_object_or_404(PaymentOrders, id=pk)
    instance.is_paid = True
    instance.save()
    messages.success(request, 'The order is paid.')
    return HttpResponseRedirect(reverse('inventory:vendor_detail', kwargs={'pk': instance.object_id}))
