from django.shortcuts import HttpResponseRedirect, redirect, get_object_or_404 ,render
from django.template.loader import render_to_string
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, DetailView, TemplateView, UpdateView, FormView
from django.contrib.auth.models import User
from django.template.context_processors import csrf
from django.db.models import Q
from django.contrib import messages
from django.db.models import Avg, Sum
from django.views.decorators.csrf import csrf_exempt

import json

import datetime
from account.models import *
from .tools import *
from .models import *
from .forms import *
from dashboard.forms import *
from account.forms import CreateCostumerPosForm


class HomePage(ListView):
    template_name = 'PoS/homepage.html'
    model = RetailOrder

    def get_queryset(self):
        queryset = RetailOrder.objects.all()[:50]
        return queryset


@staff_member_required()
def create_new_sales_order(request):
    user = request.user
    user_account = ExtendsUser.objects.get(user=user)
    new_order = RetailOrder.objects.create(costumer_account=CostumerAccount.objects.first())
    if user_account:
        new_order.seller_account = user
        if user_account.store_related:
            new_order.store_related = user_account.store_related
    new_order.save()
    new_order.title = 'Sale %s' % new_order.id
    new_order.save()
    return HttpResponseRedirect('/point-of-sale/sales/%s' % new_order.id)


@staff_member_required()
def create_return_order(request):
    user = request.user
    user_account = ExtendsUser.objects.get(user=user)
    new_order = RetailOrder.objects.create(order_type='b')
    if user_account:
        new_order.seller_account = user
        if user_account.store_related:
            new_order.store_related = user_account.store_related
        return HttpResponseRedirect('/point-of-sale/sales/%s' % new_order.id)


@staff_member_required()
def sales(request, pk):
    # initial_data
    object_list = Product.my_query.active_warehouse()
    object = get_object_or_404(RetailOrder, id=pk)
    is_sale = object.is_sale()
    form = SalesForm(instance=object)
    if request.POST:
        form = SalesForm(request.POST, instance=object)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('pos:sales', kwargs={'pk': pk}))
        form_paid = PaymentForm(request.POST)
        if form_paid.is_valid():
            form_paid.save()
            return HttpResponseRedirect(reverse('pos:sales', kwargs={'pk': pk}))
    object_list = object_list[:10]
    context = locals()
    return render(request, 'PoS/sales.html', context)


class SalesPoS(ListView):
    model = Product
    form_class = SalesForm
    template_name = 'PoS/sales.html'
    paginate_by = 10
    object = None

    def get_queryset(self):
        queryset = Product.my_query.active_warehouse()
        return queryset

    def get_context_data(self, **kwargs):
        context = super(SalesPoS, self).get_context_data(**kwargs)
        self.object = object = get_object_or_404(RetailOrder, id=self.kwargs['pk'])
        is_sale = True if self.object.order_type == 'r' else False
        payment_orders = self.object.payorders.all()
        form = self.form_class(instance=self.object)
        context.update(locals())
        return context

    def post(self, request, *args, **kwargs):
        form_order = SalesForm(request.POST, instance=self.object)
        if form_order.is_valid():
            form_order.save()
            return HttpResponseRedirect(reverse('pos:sales', kwargs={'pk': self.kwargs['pk']}))
        form = PaymentForm(request.POST, None)
        if form.is_valid():
            print('form_payment')
            form.save()
        return HttpResponseRedirect(reverse('pos:sales', kwargs={'pk': self.kwargs['pk']}))


@staff_member_required()
def ajax_products_search(request, pk):
    data = dict()
    order = get_object_or_404(RetailOrder, id=pk)
    is_sale = True if order.order_type == 'r' else False
    search_name = request.GET.get('search_name')
    products = None
    if len(search_name) >= 3:
        products = Product.my_query.active_warehouse()
        products = products.filter(Q(title__icontains=search_name) |
                                   Q(supply__title__icontains=search_name) |
                                   Q(brand__title__icontains=search_name) |
                                   Q(category__title__icontains=search_name) |
                                   Q(color__title__icontains=search_name)
                                   ).distinct()[:10]
        print(products.count())
    data['products'] = render_to_string(request=request,
                                        template_name='PoS/ajax/products_search.html',
                                        context={'object_list': products,
                                                 'object': order,
                                                 'is_sale': is_sale
                                                 }
                                        )

    return JsonResponse(data)


@staff_member_required()
def ajax_add_product(request, dk, pk):
    data = dict()
    order = get_object_or_404(RetailOrder, id=dk)
    product = get_object_or_404(Product, id=pk)
    qty = request.GET.get('qty')
    order_item_exists = RetailOrderItem.objects.filter(title=product, order=order)
    if order_item_exists:
        order_item = order_item_exists.last()
        order_item.qty += Decimal(qty)
        order_item.save()
    else:
        create_item = RetailOrderItem.objects.create(title=Product.objects.get(id=pk),
                                                     order=order,
                                                     cost=product.price_buy,
                                                     price=product.price,
                                                     qty=Decimal(qty),
                                                     discount=product.price_discount,
                                                     )
        create_item.save()
    data['order_details'] = render_to_string(request=request,
                                             template_name='PoS/ajax/add_product.html',
                                             context={'object': order})
    return JsonResponse(data)


@staff_member_required()
def ajax_edit_product(request, dk):
    data = dict()
    product = get_object_or_404(RetailOrderItem, id=dk)
    get_type = request.GET.get('type')
    print(get_type)
    if get_type == 'add':
        product.qty += 1
    else:
        if product.qty >1:
            product.qty -= 1
    product.save()
    order = product.order
    data['order_details'] = render_to_string(request=request,
                                             template_name='PoS/ajax/add_product.html',
                                             context={'object': order})
    return JsonResponse(data)


@staff_member_required()
def ajax_delete_product(request, dk):
    data = dict()
    product = get_object_or_404(RetailOrderItem, id=dk)
    order = product.order
    product.delete()
    data['order_details'] = render_to_string(request=request,
                                             template_name='PoS/ajax/add_product.html',
                                             context={'object': order})
    return JsonResponse(data)

#  actions


@staff_member_required()
def order_paid(request, pk):
    order = get_object_or_404(RetailOrder, id=pk)
    order.is_paid = True
    order.save()
    return HttpResponseRedirect('/point-of-sale/')


def AuthorCreatePopup(request):
    form = CreateCostumerPosForm(request.POST or None)
    if form.is_valid():
        instance = form.save()

        ## Change the value of the "#id_author". This is the element id in the form

        return HttpResponse(
            '<script>opener.closePopup(window, "%s", "%s", "#id_costumer_account");</script>' % (instance.pk, instance))

    return render(request, "PoS/popup/costumer_form.html", {"form": form})


def AuthorEditPopup(request, pk=None):
    instance = get_object_or_404(CostumerAccount, pk=pk)
    form = CreateCostumerPosForm(request.POST or None, instance=instance)
    if form.is_valid():
        instance = form.save()

        ## Change the value of the "#id_author". This is the element id in the form

        return HttpResponse(
            '<script>opener.closePopup(window, "%s", "%s", "#id_author");</script>' % (instance.pk, instance))

    return render(request, "PoS/popup/costumer_form.html", {"form": form})


@csrf_exempt
def get_author_id(request):
    if request.is_ajax():
        author_name = request.GET['author_name']
        author_id = CostumerAccount.objects.get(name=author_name).id
        data = {'author_id': author_id, }
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")


def ajax_payment_add(request, pk):
    data = dict()
    get_order = get_object_or_404(RetailOrder, id=pk)
    form = PaymentForm(initial={'payment_type': get_order.payment_method,
                                'is_expense': False,
                                'is_paid': True,
                                'date_expired': datetime.datetime.now(),
                                'title': 'Αποπληρωμή %s' % get_order,
                                'value': get_order.final_price- get_order.paid_value,
                                'content_type': ContentType.objects.get_for_model(RetailOrder),
                                'object_id': pk
                                })
    data['add_payment'] = render_to_string(request=request,
                                           template_name='PoS/ajax/payment.html',
                                           context=locals()
                                           )
    return JsonResponse(data)