from django.shortcuts import HttpResponseRedirect, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, UpdateView

from .models import *
from .forms import *
from account.models import *


@staff_member_required
def create_warehouse_income_order(request):
    user = request.user
    new_order = RetailOrder.objects.create(costumer_account=CostumerAccount.objects.first())
    try:
        user_account = ExtendsUser.objects.get(user=user)
        new_order.seller_account = user
        if user_account.store_related:
            new_order.store_related = user_account.store_related
    except:
        user_account = None
    new_order.order_type = 'wa'
    new_order.title = 'Παραστατικο Εισαγωγής %s' % new_order.id
    new_order.save()
    return HttpResponseRedirect(reverse('pos:warehouse_in', kwargs={'dk': new_order.id}))


@method_decorator(staff_member_required, name='dispatch')
class WarehouseOrderInPage(ListView):
    model = Product
    template_name = 'warehouse_pos/index_pos.html'

    def get_queryset(self):
        queryset = Product.objects.filter(active=True)

        return queryset

    def get_context_data(self, **kwargs):
        context = super(WarehouseOrderInPage, self).get_context_data(**kwargs)

        return context