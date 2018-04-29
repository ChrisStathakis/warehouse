from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from products.forms_popup import *
import json


def category_create(request):
    print('here')
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
        return HttpResponse(
            '<script>opener.closePopup(window, "%s", "%s", "#id_author");</script>' % (instance.pk, instance))
    return render(request, "dashboard/ajax_calls/popup_form.html", {"form": form})


def category_edit(request, pk=None):
    instance = get_object_or_404(Category, id=pk)
    form = CategoryForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return HttpResponse('<script>opener.closePopup(window, "%s", "%s", "#id_author");</script>' %
                            (instance.pk, instance))
    return render(request, 'dashboard/ajax_calls/popup_form.html', {"form": form})


@csrf_exempt
def get_category_id(request):
    if request.is_ajax():
        category_name = request.GET.get('cate_name')
        category_id = Category.objects.get(title=category_name).id
        data = {'category_id': category_id,}
        return JsonResponse(data)
    return HttpResponse("/")


def product_action(action_type):
    pass


def grab_orders_filter_data(request):
    not_paid_name = request.GET.get('not_paid_name', None)
    paid_name = request.GET.get('paid_name', None)
    printed_name = request.GET.get('printed_name', None)
    status_name = request.GET.getlist('status_name', None)
    payment_name = request.GET.getlist('payment_type_name', None)
    return not_paid_name, paid_name, printed_name, status_name, payment_name

#  print views

def print_order(request, dk):
    pass