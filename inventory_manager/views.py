from django.shortcuts import render, HttpResponseRedirect, redirect, reverse, get_object_or_404
from django.views.generic import ListView, DetailView, UpdateView, FormView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType

from products.models import Supply, Category, Color, Size
from products.forms import VendorForm
from .models import Order
from dashboard.models import PaymentOrders
from dashboard.forms import PaymentForm


@method_decorator(staff_member_required, name='dispatch')
class VendorPageList(ListView):
    template_name = 'inventory_manager/vendor_list.html'
    model = Supply
    paginate_by = 20

    def get_queryset(self):
        queryset = Supply.objects.all()
        search_name = self.request.GET.get('search_name', None)
        queryset = queryset.filter(Q(title__icontains=search_name)| 
                                   Q(afm__icontains=search_name) |
                                   Q(phone__icontains=search_name) |
                                   Q(phone1__icontains=search_name) |
                                   Q(email__icontains=search_name)
                                  ).distinct() if search_name else queryset
        return queryset

    def get_context_data(self, **kwargs):
        context = super(VendorPageList, self).get_context_data(**kwargs)
        search_name = self.request.GET.get('search_name', None)
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
        queryset = queryset.filter(Q(code__icontains=search_name) |
                                   Q(vendor__title__icontains=search_name) |
                                   Q(notes__icontains=search_name)
                                  ).distinct() if search_name else queryset
        queryset = queryset.filter(is_paid=False) if paid_name else queryset
        return queryset

    def get_context_data(self, **kwargs):
        context = super(WarehousePaymentPage, self).get_context_data(**kwargs)
        search_name = self.request.GET.get('search_name', None)
        paid_name = self.request.GET.get('paid_name', None)
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