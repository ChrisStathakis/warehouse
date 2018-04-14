from django.shortcuts import render,HttpResponseRedirect, redirect
from django.views.generic import ListView, DetailView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required


from products.models import Supply, Category, Color, Size


@method_decorator(staff_member_required, name='dispatch')
class VendorPage(ListView):
    template_name = ''
    model = Supply
    paginate_by = 10

    def get_context_data(self):
        queryset = Supply.objects.all()
        return queryset


@method_decorator(staff_member_required, name='dispatch')
class CategoryPage(ListView):
    template_name = ''
    model = Category
    paginate_by = 10

    def get_context_data(self):
        queryset = Category.objects.all()
        return queryset

    