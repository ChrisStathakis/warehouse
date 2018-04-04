from django.shortcuts import render, HttpResponse, HttpResponseRedirect, get_object_or_404
from django.core import serializers
from django.db.models import Q
from django.views.generic import RedirectView
from django.http import JsonResponse
from .forms import *
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import json


def create_costumer(request, dk):
    form = CostumerForm(request.POST or None)
    if request.POST:
        if form.is_valid():
            order = RetailOrder.objects.get(id=dk)
            old_costumer = order.costumer_account
            old_costumer.balance -= order.get_total_value - order.paid_value
            old_costumer.paid_value -= order.paid_value
            old_costumer.total_order_value -= order.get_total_value
            old_costumer.save()
            instance = form.save()
            #instance.refresh_from_db()
            instance.balance += order.get_total_value - order.paid_value
            instance.paid_value += order.paid_value
            instance.total_order_value += order.get_total_value
            instance.save()
            order.costumer_account = instance
            order.save()
            return HttpResponse(
                '<script>opener.closePopup(window, "%s", "%s", "#id_costumer");</script>' % (instance.pk, instance))
    context = locals()
    return render(request, 'inventory/create_costumer_form.html', context)


@csrf_exempt
def get_costumer_id(request):
    if request.is_ajax():
        costumer_name = request.GET.get('costumer_name')
        costumer_id = CostumerAccount.objects.get('')
        data = {}


def ajax_add_item_auto(request, dk, pk):
    order = get_object_or_404(RetailOrder, id=dk)
    product = get_object_or_404(Product, id=pk)
    p_qs = RetailOrderItem.objects.filter(order=order, title=product)
    if p_qs.exists() and p_qs.count() == 1:
        retail_item = p_qs.first()
        retail_item.qty += 1
        retail_item.save()
    else:
        retail_item = RetailOrderItem.objects.create(order=order,
                                                     title=product,
                                                     qty=1,
                                                     price=product.site_price,
                                                     cost=product.price_buy,
                                                     )
    #retail_item.add_item_auto()
    retail_items = RetailOrderItem.objects.filter(order=order)
    order.refresh_from_db()
    data = {}
    for item in retail_items:
        data[str(item.title)] = [item.title.title, item.price, item.qty, item.title.get_categoty_title, item.title.get_supplier_title, item.id]
        data[order.title] = ['order', order.tag_remaining_value(), order.tag_total_value(), order.paid_value]
    #data[str(order.title)] = [order.value, order.remaining_value()]
    return JsonResponse(data, safe=False)


def ajax_delete_item_auto(request, dk):
    retail_order_item = RetailOrderItem.objects.get(id=dk)
    order = retail_order_item.order
    retail_order_item.delete_from_order()
    retail_order_item.delete()
    order.refresh_from_db()
    get_items = order.retailorderitem_set.all()
    data = {}
    for item in get_items:
        data[str(item.title)] = [item.title.title, item.price, item.qty, item.title.get_categoty_title, item.title.get_supplier_title, item.id]
        data[order] = [order.get_remaining_value, order.get_total_value, order.paid_value]
    return JsonResponse(data, safe=False)


def ajax_search_products(request):
    q = request.GET.get('search_products')
    if not len(q) > 3:
        return JsonResponse({}, safe=False)
    products = Product.my_query.active_warehouse().filter(Q(title__contains=q) |
                                                          Q(category__title__contains=q) |
                                                          Q(supplier__title__contains=q)
                                                          ).distinct()[:6]
    data = {}
    for product in products:
        data[product.title] = [product.id, products.sku, product.title, product.get_categoty_title, product.get_supplier_title, product.price]
    return JsonResponse(data, safe=False)







