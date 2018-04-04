from django.shortcuts import render, HttpResponseRedirect, redirect, get_object_or_404, render_to_response
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from django.template.context_processors import csrf
from django.db.models import Q
from django.contrib import messages
from django.db.models import Avg, Sum
from django.contrib.auth.models import User
from account.forms import CostumerAccount, CreateCostumerPosForm
from account.models import CostumerAccount


from .tools import *
from dateutil.relativedelta import relativedelta

from .models import *
from mysite.models import CompanyInfo
from .forms import *
from tools.views import date_pick_session


def eshop_filter(query, querylist, date_start, date_end):
    new_query = querylist.filter(Q(title__contains=query) |
                                           Q(notes__contains=query) |
                                           Q(first_name__contains=query) |
                                           Q(last_name__contains=query) |
                                           Q(city__contains=query) |
                                           Q(address__contains=query) |
                                           Q(state__contains=query) |
                                           Q(zip_code__contains=query) |
                                           Q(cellphone__contains=query) |
                                           Q(phone__contains=query) |
                                           Q(email__contains=query) |
                                           Q(state__contains=query)
                                           ).distinct()
    new_query = querylist.filter(day_created__range=[date_start, date_end])
    return new_query


@staff_member_required
def eshop_homepage(request):
    date_end = datetime.datetime.now()
    date_start = date_end - relativedelta(days=10)
    new_orders = RetailOrder.my_query.eshop_new_orders()
    orders_in_progress = RetailOrder.my_query.eshop_orders_on_progress()
    orders_done = RetailOrder.my_query.eshop_done_orders(date_start, date_end)
    if request.POST:
        query = request.POST.get('query')
        date_pick = request.POST.get('date_pick')
        if date_pick:
            check_date = date_pick_session(request)
            if check_date:
                date_start, date_end, date_string = check_date
                orders_done = RetailOrder.my_query.eshop_done_orders(date_start, date_end)
        if query:
            new_orders = eshop_filter(query, new_orders, date_start, date_end)
            orders_in_progress = eshop_filter(query, orders_in_progress, date_start, date_end)
            orders_done = eshop_filter(query, orders_done, date_start, date_end)
    context = locals()
    context.update(csrf(request))
    return render(request, 'PoS/eshop/homepage.html', context)


@staff_member_required
def create_new_eshop_order(request):
    new_order = RetailOrder.objects.create(order_type='e',
                                           status=OrderStatus.objects.first(),
                                           costumer_account=CostumerAccount.objects.first(),
                                           seller_account=request.user,
                                           )
    new_order.save()
    new_order.refresh_from_db()
    return redirect('eshop_new_order', dk=new_order.id)


# main eshop page
@staff_member_required
def eshop_new_order(request, dk):
    eshop_order = get_object_or_404(RetailOrder, id=dk)
    cart_items = eshop_order.retailorderitem_set.all()
    costumers = CostumerAccount.objects.all()
    payment_methods = PaymentMethod.my_query.active_and_site()
    brands = Brands.objects.all()
    main_categories = CategorySite.objects.filter(parent=None)
    products = Product.my_query.active_with_qty()
    request.session['new_order'] = 0
    shipping = Shipping.objects.filter(active=True)
    if request.GET:
        cate_name = request.GET.getlist('cate_name')
        query = request.GET.get('search_pro')
        if query:
            products = products.filter(Q(title__contains=query) |
                                       Q(sku__contains=query) |
                                       Q(brand__title__contains=query) |
                                       Q(category__title__contains=query)
                                       ).distinct()
            if cate_name:
                products = products.filter(category_site__id__in=cate_name)
    if 'submit_order' in request.POST:
        get_new_payment = request.POST.get('payment_name')
        get_new_shipping = request.POST.get('shipping_name')
        if get_new_shipping:
            shipping_instance = get_object_or_404(Shipping, id=get_new_shipping)
            eshop_order.shipping = shipping_instance
            eshop_order.save()
        if get_new_payment:
            payment_instance = get_object_or_404(PaymentMethod, id=get_new_payment)
            eshop_order.payment_method = payment_instance
            eshop_order.save()
        return redirect('eshop_new_order', dk=dk)
    if 'search_fil' in request.POST:
        brand_name = request.POST.getlist('brand_name')
        category_name = request.POST.getlist('main_cat')
        if brand_name:
            products = products.filter(brand__id__in=brand_name)
        if category_name:
            products = products.filter(category__id__in=category_name)

    if 'new_costumer' in request.POST:
        form_new_costumer = EshopFormCostumer(request.POST, instance=eshop_order)
        if form_new_costumer.is_valid():
            form_new_costumer.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        form_new_costumer = EshopFormCostumer(instance=eshop_order)
    currency = CURRENCY
    paginator = Paginator(products, 50)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    context = locals()
    context.update(csrf(request))
    return render(request, 'PoS/eshop/eshop_order_section.html', context)


@staff_member_required
def eshop_change_costumer(request, dk, pk):
    order = get_object_or_404(RetailOrder, id=dk)
    old_costumer = order.costumer_account
    costumer = get_object_or_404(CostumerAccount, id=pk)
    order.change_costumer_from_history(new_costumer=costumer, old_costumer=old_costumer)
    order.save()
    return redirect('eshop_new_order', dk=dk)


@staff_member_required
def eshop_print_order(request, dk):
    currency = CURRENCY
    company = CompanyInfo.objects.last()
    order = get_object_or_404(RetailOrder, id=dk)
    order_items = order.retailorderitem_set.all()
    context = locals()
    return render(request, 'PoS/eshop/eshop_print_template.html', context)


@staff_member_required
def eshop_add_product(request, dk, pk):
    eshop_order = get_object_or_404(RetailOrder, id=dk)
    product = get_object_or_404(Product, id=pk)
    form = RetailAddForm(request.POST or None, initial={'order': eshop_order,
                                                        'price': product.site_price,
                                                        'title': product,
                                                        'cost': product.price_buy,
                                                        })
    if request.POST:
        if form.is_valid():
            form.save()
            form.add_item(order=eshop_order, product=product)
            return redirect('eshop_new_order', dk=dk)
    return_page = request.META.get('HTTP_REFERER')
    eshop_order =True
    context = locals()
    context.update(csrf(request))
    return render(request, 'inventory/create_costumer_form.html', context)


@staff_member_required
def eshop_edit_product(request, dk):
    order_item = get_object_or_404(RetailOrderItem, id=dk)
    order = order_item.order
    old_order_price = order_item.price
    old_order_qty = order_item.qty
    old_cost = order_item.cost
    if request.POST:
        form = RetailAddForm(request.POST, instance=order_item)
        if form.is_valid():
            form.save()
            form.edit_item(order_item=order_item, old_price=old_order_price, old_qty=old_order_qty, old_cost=old_cost)
            return redirect('eshop_new_order', dk=order.id)
    else:
        form = RetailAddForm(instance=order_item)
    context = {
        'form': form,
        'order': order_item.order,
        'order_item': order_item,
        'return_page': request.META.get('HTTP_REFERER')
    }
    context.update(csrf(request))
    return render(request, 'inventory/create_costumer_form.html', context)


@staff_member_required
def eshop_delete_product(request, dk):
    order_item = get_object_or_404(RetailOrderItem, id=dk)
    order = order_item.order
    order_item.delete_from_order()
    order_item.delete()
    return redirect('eshop_new_order', dk=order.id)


@staff_member_required
def eshop_is_find(request, dk):
    get_order_item = get_object_or_404(RetailOrderItem, id=dk)
    order = get_order_item.order
    if order.status.id == 1:
        order.status = OrderStatus.objects.get(id=2)
        order.save()
    if get_order_item.is_find:
        get_order_item.is_find = False
    else:
        get_order_item.is_find = True
    get_order_item.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@staff_member_required
def eshop_edit_order(request, dk):
    order = get_object_or_404(RetailOrder, id=dk)
    if request.POST:
        form = EshopEditForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('eshop_new_order', dk=dk)
    form = EshopEditForm(instance=order)
    return_page = request.META.get('HTTP_REFERER')
    context = locals()
    context.update(csrf(request))
    return render(request, 'inventory/create_costumer_form.html' ,context)


@staff_member_required
def eshop_change_order_status(request, dk):
    order = get_object_or_404(RetailOrder, id=dk)
    if request.POST:
        form = RetailChangeStatus(request.POST, instance=order)
        if form.is_valid():
            form.save()
            form.update_retail_items(dk)
            return redirect('eshop_new_order', dk=dk)
    else:
        form = RetailChangeStatus(instance=order)
    return_page = request.META.get('HTTP_REFERER')
    context = locals()
    context.update(csrf(request))
    return render(request, 'inventory/create_costumer_form.html', context)


def eshop_ajax_search(request, dk):
    eshop_order = get_object_or_404(RetailOrder, id=dk)
    if request.POST:
        get_title = request.POST.get('search_text')
    else:
        get_title = ''
    costumers = CostumerAccount.objects.all()
    if len(get_title) > 2:
        costumers = costumers.filter(Q(first_name__contains=get_title) |
                                     Q(last_name__contains=get_title) |
                                     Q(shipping_address_1__contains=get_title) |
                                     Q(shipping_city__contains=get_title) |
                                     Q(phone__contains=get_title) |
                                     Q(cellphone__contains=get_title)
                                     ).distinct()
    return render_to_response('PoS/ajax_templates/results.html', {'costumers': costumers,
                                                                  'eshop_order': eshop_order,
                                                                  })


@staff_member_required
def orders_management(request):
    orders = RetailOrder.my_query.eshop_orders()
    orders_a = orders.exclude(status_id=7)
    orders_items = RetailOrderItem.objects.filter(order__in=orders_a)
    order_items_found = orders_items.filter(is_find=True)
    order_items_not_found = orders_items.filter(is_find=False)
    order_status = OrderStatus.objects.all()
    new_orders = orders.filter(status__id=1)
    order_in_progress = orders.filter(status__id=2)
    orders_ready_to_go = orders.filter(status__id=5)
    orders_sent = orders.filter(status__id=6)
    orders_get_paid = orders.filter(status_id=7)
    orders_in_waiting = orders.filter(status__id__in=[3,4])
    context = {
        'new_orders':new_orders,
        'status':order_status,
        'orders_in_progress':order_in_progress,
        'orders_ready_to_go':orders_ready_to_go,
        'orders_sent':orders_sent,
        'orders_in_waiting':orders_in_waiting,
        'order_items':orders_items,
        'order_items_found':order_items_found,
        'order_items_not_found':order_items_not_found,
        'order_get_paid':orders_get_paid,
    }
    return render(request, 'PoS/eshop/eshop_order_management.html', context)


@staff_member_required
def orders_management_details(request, dk):
    orders = RetailOrder.my_query.eshop_orders()
    orders_a = orders.exclude(status_id =7)
    order_status = OrderStatus.objects.all()
    new_orders = orders.filter(status__id=1)
    order_in_progress = orders.filter(status__id=2)
    orders_ready_to_go = orders.filter(status__id=5)
    orders_sent = orders.filter(status__id=6)
    orders_get_paid = orders.filter(status_id=7)
    orders_in_waiting = orders.filter(status__id__in=[3,4])
    order = RetailOrder.objects.get(id=dk)
    orders_items = RetailOrderItem.objects.filter(order=order)
    order_items_found = orders_items.filter(is_find=True)
    order_items_not_found = orders_items.filter(is_find=False)
    context ={
        'new_orders': new_orders,
        'status': order_status,
        'orders_in_progress': order_in_progress,
        'orders_ready_to_go': orders_ready_to_go,
        'orders_sent': orders_sent,
        'orders_in_waiting': orders_in_waiting,
        'order_items': orders_items,
        'order_items_found': order_items_found,
        'order_items_not_found': order_items_not_found,
        'order_get_paid': orders_get_paid,
    }
    return render(request, 'PoS/eshop/eshop_order_management.html', context)


@staff_member_required
def orders_management_change(request,dk,pk):
    order = RetailOrder.objects.get(id=dk)
    new_status = OrderStatus.objects.get(id=pk)
    order.status = new_status
    order.save()
    if int(pk) == 5:
        order_items = order.retailorderitem_set.all()
        for item in order_items:
            item.is_find = True
            item.save()
    if int(pk) == 6:
        order_items = order.retailorderitem_set.all()
        for item in order_items:
            item.is_find = True
            item.save()
    if int(pk) == 7:
        order_items = order.retailorderitem_set.all()
        for item in order_items:
            item.is_find = True
            item.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@staff_member_required
def orders_management_product_change(request,dk):
    item= RetailOrderItem.objects.get(id=dk)
    if item.is_find:
        item.is_find=False
        item.save()
        order = item.order
        order.status = OrderStatus.objects.get(id=2)
        order.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        item.is_find =True
        item.save()
        order = item.order
        order.status = OrderStatus.objects.get(id=2)
        order.save()
        order_items = order.retailorderitem_set.all()
        for ele in order_items:
            if ele.is_find:
                continue
            else:
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        order.status = OrderStatus.objects.get(id=5)
        order.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

