from django.shortcuts import render
from django.views.generic import ListView, DetailView, View, CreateView
from django.db.models import Q, Sum

from products.models import *
from products.forms import *
from point_of_sale.models import *
from transcations.models import *

from decimal import Decimal

class StoresReport(ListView):
	model = Store
	template_name = 'dashboard/templates/reports/total_reports/stores_report.html'


	def get_context_data(self, **kwargs):
		context = super(StoresReport, self).get_context_data(**kwargs)
		currency = CURRENCY
		stores = self.object_list
		data = {}
		for ele in stores:
			payroll_orders = PayrollInvoice.objects.filter(person__store_related=ele)
			fixed_costs = FixedCostInvoice.objects.filter(category__store_related=ele)
			incomes = RetailOrder.objects.filter(store_related=ele)
			payroll = payroll_orders.aggregate(Sum('paid_value'))['paid_value__sum'] if payroll_orders else 0
			fixed_costs_ = fixed_costs.aggregate(Sum('paid_value'))['paid_value__sum'] if fixed_costs else 0
			incomes_ = incomes.aggregate(Sum('paid_value'))['paid_value__sum'] if incomes else 0
			warehouse_orders = round(Decimal(incomes_)/Decimal(1.82), 2)
			diff = incomes_ - payroll - fixed_costs_ - warehouse_orders
			data[ele] = [payroll, fixed_costs_, warehouse_orders, incomes_, diff]
		print(payroll)
		context.update(locals())
		return context

	
