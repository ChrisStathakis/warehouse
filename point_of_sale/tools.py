from django.shortcuts import HttpResponseRedirect
from django.db.models import Q
from .models import RetailOrder
from account.models import CostumerAccount
from decimal import Decimal


# in this function we update anything that is related to order_item from vendor to warehouse etc
def return_item_qty_change(order_item, qty=None ):
    price = order_item.price
    cost = order_item.cost
    if qty:
        qty = Decimal(qty)
    create_order = RetailOrder.objects.create(order_type=order_item.order.order_type,
                                              costumer_account = order_item.order.costumer_account,
                                              payment_method = order_item.order.payment_method,
                                              taxes = order_item.order.taxes,
                                              )
    create_order.save()
    order_item.id= None
    order_item.save()
    # until now i created a new order and a new item, now i modify the item
    # to meet the requirements of the return
    order_item.qty = order_item.qty * (-1)
    if qty:
        order_item.qty = qty*(-1)

    order_item.price = price
    order_item.cost = cost
    order_item.order = create_order
    order_item.is_return = True
    order_item.save()

    create_order.value -= order_item.total_price_number()
    create_order.total_cost -= order_item.total_cost()
    create_order.save()

    order_item.title.reserve += abs(order_item.qty)
    order_item.title.save()


def order_change_costumer(request, retail_order):
    get_order_status = retail_order.status.id
    new_costumer = request.POST.get('edit_cost')
    if get_order_status in [7, 9]:
        retail_order.paid_value = 0
        retail_order.save()
    if retail_order.order_type == 'e' or retail_order.order_type == 'r':
        #removes the association from the old costumer
        retail_order.costumer_account.balance -= retail_order.value - retail_order.paid_value
        retail_order.costumer_account.paid_value -= retail_order.paid_value
        retail_order.costumer_account.total_order_value -= retail_order.value
        retail_order.costumer_account.save()
        #add the values to new costumer
        retail_order.costumer_account = CostumerAccount.objects.get(id=new_costumer)
        retail_order.costumer_account.balance += retail_order.value - retail_order.paid_value
        retail_order.costumer_account.paid_value += retail_order.paid_value
        retail_order.costumer_account.total_order_value += retail_order.value
        retail_order.costumer_account.save()
        retail_order.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    elif retail_order.order_type == 'b':
        #removes the association from the old costumer
        retail_order.costumer_account.total_order_value += retail_order.value
        retail_order.costumer_account.paid_value += retail_order.value
        retail_order.costumer_account.save()
        #add the values to new costumer
        retail_order.costumer_account = CostumerAccount.objects.get(id=new_costumer)
        retail_order.save()
        retail_order.refresh_from_db()
        retail_order.costumer_account.total_order_value -= retail_order.value
        retail_order.costumer_account.paid_value -= retail_order.value
        retail_order.costumer_account.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def order_change_payment_method(request, retail_order):
    payment_name = request.POST.get('payment_name')
    # retail_order.payment_method = PaymentMethod.objects.get(id=payment_name)
    retail_order.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def close_order(request, order):
    if order.order_type == 'r' or order.order_type == 'e':
        old_paid_value = order.paid_value
        order.costumer_account.balance += old_paid_value
        order.costumer_account.save()
        order.paid_value = order.value
        order.save()
        order.costumer_account.balance -= order.value
        order.costumer_account.save()
        # order.status = OrderStatus.objects.get(id=7)
        order.save()
    if order.order_type == 'b':
        if int(order.paid_value) == 0:
            order.paid_value = order.value
       #  order.status = OrderStatus.objects.get(id=8)
        order.save()


def order_change_status():
    pass


def orders_filter(request, orders):
    search_pro, costumers, payments = None, None, None
    if request.GET:
        search_pro = request.GET.get('search_pro')
        costumers = request.GET.get('costumer_name')
        payments = request.GET.get('payment_name')
        date_pick = request.GET.get('date_pick')
        if search_pro:
            orders = orders.filter(Q(title__contains=search_pro) |
                                   Q(notes__contains=search_pro) |
                                   Q(costumer_account__first_name__contains=search_pro) |
                                   Q(costumer_account__last_name__contains=search_pro)
                                   ).distinct()
        if costumers:
            orders = orders.filter(costumer_account__id=costumers)
        if payments:
            orders = orders.filter(payment_method__id=payments)
        if date_pick:
            date_start, date_end = date_pick_form(request, date_pick)
            orders = orders.filter(day_created__range=[date_start, date_end])
    return orders, search_pro, costumers, payments




