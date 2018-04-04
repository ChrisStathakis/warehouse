from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
import json

from products.forms import BrandForm, CategoryForm
from products.models import Brands


def createBrandPopup(request):
    form = BrandForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
        return HttpResponse(
            '<script>opener.closePopup(window, "%s", "%s", "#id_brand");</script>' % (instance.pk, instance))
    return render(request, 'dashboard/ajax_calls/popup_form.html', {"form": form})


def createCategoryPopup(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
        return HttpResponse(
            '<script>opener.closePopup(window, "%s", "%s", "#id_category");</script>' % (instance.pk, instance))
    return render(request, 'dashboard/ajax_calls/popup_form.html', {"form": form})


def get_brand_id(request):
    if request.is_ajax():
        author_name = request.GET['author_name']
        author_id = Brands.objects.get(title=author_name).id
        data = {'author_id': author_id, }
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse("/")

