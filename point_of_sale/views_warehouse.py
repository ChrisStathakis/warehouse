from django.shortcuts import HttpResponseRedirect, redirect, get_object_or_404, reverse
from django.template.loader import render_to_string
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, UpdateView
from django.shortcuts import render
from .models import *
from .forms import *
from account.models import *


@staff_member_required
def create_warehouse_income_order(request):
    user = request.user
    new_order = RetailOrder.objects.create(costumer_account=CostumerAccount.objects.first(),
                                           status='2',
                                           order_type='wa',
                                           title='Test',
                                           )
    try:
        user_account = ExtendsUser.objects.get(user=user)
        new_order.seller_account = user
        if user_account.store_related:
            new_order.store_related = user_account.store_related
    except:
        user_account = None
    new_order.title = 'Παραστατικο Εισαγωγής %s' % new_order.id
    new_order.save()
    return HttpResponseRedirect(reverse('pos:warehouse_in', kwargs={'dk': new_order.id}))


@staff_member_required
def warehouse_order_in(request, dk):
    object_list = Product.my_query.active_warehouse()
    object = get_object_or_404(RetailOrder, id=dk)
    print(object.order_type)
    form = RetailOrderWarehouseIncomeForm(request.POST or None, instance=object)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('pos:warehouse_in', kwargs={'dk': dk}))
    context = locals()
    return render(request, 'warehouse_pos/index_pos.html', context)


@staff_member_required
def warehouse_save(request, dk):
    instance = get_object_or_404(RetailOrder, id=dk)
    instance.save()
    return HttpResponseRedirect(reverse('pos:homepage'))
