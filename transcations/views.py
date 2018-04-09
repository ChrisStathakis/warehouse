from django.views.generic import ListView, DetailView, TemplateView, FormView
from django.shortcuts import get_object_or_404, HttpResponseRedirect, reverse, render
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages


from .models import *
from .forms import CreateBillForm, CreatePayrollForm, CreateBillCategoryForm
from dashboard.forms import PaymentForm


@method_decorator(staff_member_required, name='dispatch')
class BillingPaymentPage(TemplateView):
    template_name = 'billings/index.html'

    def get_context_data(self, **kwargs):
        context = super(BillingPaymentPage, self).get_context_data(**kwargs)
        billing_categories = FixedCosts.objects.all()
        billings = FixedCostInvoice.my_query.expiring_invoice()
        payroll = PayrollInvoice.my_query.not_paid().order_by('date_expired')
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class BillingPage(ListView):
    model = FixedCostInvoice
    template_name = 'billings/billingsList.html'
    paginate_by = 20

    def get_queryset(self):
        queryset = FixedCostInvoice.objects.all()
        bill_name = self.request.GET.getlist('bill_name', None)
        not_paid = self.request.GET.get('not_paid', None)
        queryset = queryset.filter(category__id__in=bill_name) if bill_name else queryset
        queryset = queryset.filter(is_paid=False) if not_paid else queryset
        return queryset

    def get_context_data(self, **kwargs):
        context = super(BillingPage, self).get_context_data(**kwargs)
        categories = FixedCosts.objects.all()
        context.update(locals())
        return context


@staff_member_required
def billings_invoice_edit(request, pk):
    bill_edit = True
    instance = get_object_or_404(FixedCostInvoice, id=pk)
    page_title, back_url = 'Edit %s' % instance.title, reverse('billings:billings')
    payment_orders = instance.payorders
    form = CreateBillForm(instance=instance)
    form_payment = PaymentForm(initial={'content_type': ContentType.objects.get_for_model(FixedCostInvoice),
                                        'object_id': pk,
                                        'date_expired': datetime.datetime.now(),
                                        'is_paid': True,
                                        'is_expense': True,
                                        'value': instance.get_remaining_value(),
                                        })
    if 'edit_form' in request.POST:
        form = CreateBillForm(request.POST, instance=instance)
        if form.is_valid():
            if instance.payorders:
                messages.info(request, 'You need to delete the payments first!')
            else:
                form.save()
            return HttpResponseRedirect(reverse('billings:edit_bill', kwargs={'pk': pk}))
    if 'create_payment' in request.POST:
        form = PaymentForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('billings:edit_bill', kwargs={'pk': pk}))

    context = locals()
    return render(request, 'billings/form.html', context)


@method_decorator(staff_member_required, name='dispatch')
class CreateBillPage(FormView):
    form_class = CreateBillForm
    template_name = 'billings/form.html'

    def get_context_data(self, **kwargs):
        context = super(CreateBillPage, self).get_context_data(**kwargs)
        page_title = 'Add Billing Invoice'
        back_url = reverse('billings:billings')
        context.update(locals())
        return context

    def get_success_url(self):
        return reverse('billings:home')

    def form_valid(self, form):
        if form.is_valid():
            form.save()
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class CreateBillCategory(FormView):
    model = FixedCostsItem
    template_name = 'dash_ware/form.html'
    form_class = CreateBillCategoryForm

    def get_context_data(self, **kwargs):
        context = super(CreateBillCategory, self).get_context_data(**kwargs)
        page_title = 'Create New Bill Category'
        back_url = reverse('billings:billings')
        context.update(locals())
        return context

    def form_valid(self, form):
        if form.is_valid():
            form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('billings:billings')


@staff_member_required
def billing_invoice_paid(request, dk):
    instance = get_object_or_404(FixedCostInvoice, id=dk)
    payments = instance.payorders
    form = PaymentForm(request.POST or None)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('billings:home'))
    context = locals()
    return render(request, 'billings/payment_bill_detail.html', context)


@method_decorator(staff_member_required, name='dispatch')
class BillingDetailPage(DetailView):
    model = FixedCostsItem
    template_name = ''

    def get_context_data(self, **kwargs):
        context = super(BillingDetailPage, self).get_context_data(**kwargs)
        invoices = FixedCostInvoice.objects.filter(category=self.object)
        return context


@method_decorator(staff_member_required, name='dispatch')
class PaymentPage(ListView):
    model = PayrollInvoice
    template_name = ''

    def get_queryset(self):
        pass

    def get_context_data(self, **kwargs):
        context = super(PaymentPage, self).get_context_data(**kwargs)

        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class CreatePayrollPage(FormView):
    form_class = CreatePayrollForm
    template_name = 'dash_ware/form.html'

    def get_context_data(self, **kwargs):
        context = super(CreatePayrollPage, self).get_context_data(**kwargs)
        page_title = 'Add Payroll Invoice'
        context.update(locals())
        return context

    def get_success_url(self):
        return reverse('billings:home')
