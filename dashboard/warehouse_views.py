from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, reverse, HttpResponse
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages

from products.models import Product, Vendor

from inventory_manager.models import Order, OrderItem
from inventory_manager.forms import OrderQuickForm, VendorQuickForm, WarehouseOrderForm, OrderItemForm

import datetime


@method_decorator(staff_member_required, name='dispatch')
class WareHouseOrderPage(ListView):
    template_name = 'dash_ware/index.html'
    model = Order
    paginate_by = 20

    def get_queryset(self):
        queryset = Order.objects.all()
        queryset = self.model.filter_data(self.request, queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(WareHouseOrderPage, self).get_context_data(**kwargs)
        search_name = self.request.GET.get('search_name', None)
        vendor_name = self.request.GET.getlist('vendor_name', None)
        date_start = self.request.GET.get('date_start', None)
        date_end = self.request.GET.get('date_end', None)
        vendors = Supply.objects.filter(active=True)
        context.update(locals())
        return context


@staff_member_required
def create_new_warehouse_order(request):
    form = OrderQuickForm(request.POST or None,
                          initial = {'date_created': datetime.datetime.now()}
                          )
    if form.is_valid():
        instance = form.save()
        return HttpResponseRedirect(reverse('dashboard:warehouse_order_detail', kwargs={'dk': instance.id}))
    context = locals()
    return render(request, 'dash_ware/create_order.html', context)


@staff_member_required
def quick_vendor_create(request):
    form = VendorQuickForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
        return HttpResponse(
            '<script>opener.closePopup(window, "%s", "%s", "#id_vendor");</script>' % (instance.pk, instance))
    return render(request, 'dashboard/ajax_calls/popup_form.html', {"form": form})


@staff_member_required
def warehouse_order_detail(request, dk):
    instance = get_object_or_404(Order, id=dk)
    products = Product.my_query.active_warehouse().filter(supply=instance.vendor)
    form = WarehouseOrderForm(request.POST or None, instance=instance)
    if request.POST:
        if form.is_valid():
            form.save()
            messages.success(request, 'The order Edited!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    context = locals()
    return render(request, 'dash_ware/order_detail.html', context)


@staff_member_required
def warehouse_add_order_item(request, dk, pk):
    instance = get_object_or_404(Product, id=pk)
    order = get_object_or_404(Order, id=dk)
    form = OrderItemForm(request.POST or None, initial={'product': instance,
                                                        'order': order,
                                                        'qty': 1,
                                                        'price': instance.price_buy,
                                                        'discount': instance.order_discount,
                                                        })
    if form.is_valid():
        get_product = form.cleaned_data.get('product', None)
        get_order = form.cleaned_data.get('order', None)
        exists = OrderItem.objects.filter(order=get_order, product=get_product) if get_order and get_product else None
        if exists:
            current_item = exists.first()
            qty = form.cleaned_data.get('qty', None)
            current_item.qty += int(qty)
            current_item.save()
        else:
            new_item = form.save()
        return HttpResponseRedirect(reverse('dashboard:warehouse_order_detail', kwargs={'dk': dk}))
    page_title = 'Add product %s' % instance
    context = locals()
    return render(request, 'dash_ware/form.html', context)


@staff_member_required
def edit_order_item(request, dk):
    instance = get_object_or_404(OrderItem, id=dk)
    form = OrderItemForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('dashboard:warehouse_order_detail', kwargs={'dk': instance.order.id}))
    context = locals()
    return render(request, 'dash_ware/form.html', context)


@staff_member_required
def delete_order_item(request, dk):
    instance = get_object_or_404(OrderItem, id=dk)
    instance.delete()
    return HttpResponseRedirect(reverse('dashboard:warehouse_order_edit', kwargs={'dk': instance.order.id}))