from django.views.generic import ListView, DetailView, TemplateView, FormView
from django.shortcuts import get_object_or_404, HttpResponseRedirect, reverse, render
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages


from .models import *
from .forms import CreateBillForm, CreatePayrollForm, CreateBillCategoryForm, CreatePersonForm, CreateOccupForm
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
class PayrollPage(ListView):
    model = PayrollInvoice
    template_name = 'billings/paymentList.html'
    paginate_by = 20

    def get_queryset(self):
        queryset = PayrollInvoice.objects.all()
        person_name = self.request.GET.getlist('person_name', None)
        ocup_name = self.request.GET.getlist('ocup_name', None)
        cate_name = self.request.GET.getlist('cate_name', None)
        queryset = queryset.filter(person__id__in=person_name) if person_name else queryset
        queryset = queryset.filter(person__occupation__id__in=ocup_name) if ocup_name else queryset
        queryset = queryset.filter(category__in=cate_name) if cate_name else queryset
        queryset = queryset.order_by('is_paid', 'date_expired')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(PayrollPage, self).get_context_data(**kwargs)
        persons = Person.objects.filter(active=True)
        occups = Occupation.objects.all()
        categories = PAYROLL_CHOICES
        person_name = self.request.GET.getlist('person_name', None)
        ocup_name = self.request.GET.getlist('ocup_name', None)
        cate_name = self.request.GET.getlist('cate_name', None)
        context.update(locals())
        return context

    def post(self, request, *args, **kwargs):
        ids = []
        for post_data in request.POST:
            if 'invoice' in post_data:
                ids.append(post_data.split('_')[1])
        for each_id in ids:
            invoice = PayrollInvoice.objects.get(id=each_id)
            invoice.is_paid = True
            invoice.save()
        messages.success(request, 'The payment of the invoices updated!')
        return HttpResponseRedirect(reverse('billings:payroll_page'))

@method_decorator(staff_member_required, name='dispatch')
class CreatePayrollPage(FormView):
    form_class = CreatePayrollForm
    template_name = 'billings/form.html'

    def get_context_data(self, **kwargs):
        context = super(CreatePayrollPage, self).get_context_data(**kwargs)
        page_title = 'Add Payroll Invoice'
        back_url = reverse('billings:payroll_page')
        context.update(locals())
        return context

    def get_success_url(self):
        return reverse('billings:payroll_page')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


@staff_member_required
def edit_payroll_invoice(request, dk):
    instance = get_object_or_404(PayrollInvoice, id=dk)
    payments = instance.payorders
    form = CreatePayrollForm(instance=instance)
    page_title, back_url = 'Edit %s' % instance.title, reverse('billings:payroll_page')
    duplicate_url = reverse('billings:duplicate_payroll_invoice', kwargs={'dk': dk})
    form_payment = PaymentForm(initial={'content_type': ContentType.objects.get_for_model(PayrollInvoice),
                                        'object_id': dk,
                                        'date_expired': datetime.datetime.now(),
                                        'is_paid': True,
                                        'is_expense': True,
                                        'value': instance.get_remaining_value(),
                                        })
    if 'edit_form' in request.POST:
        form = CreatePayrollForm(request.POST, instance=instance)
        if form.is_valid():
            if instance.payorders.all():
                messages.info(request, 'You need to delete the payments first!')
            else:
                form.save()
                messages.success(request, 'You edit the invoice succesfully')
                return HttpResponseRedirect(reverse('billings:payroll_page'))
    if 'create_payment' in request.POST:
        form = PaymentForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('billings:edit_bill', kwargs={'pk': dk}))
    context = locals()
    return render(request, 'billings/form.html', context)


@staff_member_required
def duplicate_payroll_invoice(request, dk):
    instance = get_object_or_404(PayrollInvoice, id=dk)
    instance.id = None
    instance.is_paid = False
    instance.save()
    instance.refresh_from_db()
    messages.success(request, 'You successfully duplicated the Payment Invoice')
    return HttpResponseRedirect(reverse('billings:edit_payroll', kwargs={'dk': instance.id}))


@method_decorator(staff_member_required, name='dispatch')
class CreatePersonPage(FormView):
    form_class = CreatePersonForm
    template_name = 'billings/form.html'

    def get_context_data(self, **kwargs):
        context = super(CreatePersonPage, self).get_context_data(**kwargs)

        context.update(locals())
        return context

    def get_success_url(self):
        return reverse('billings:payroll_page')

    def form_valid(self, form):
        if form.is_valid():
            form.save()
            messages.success(self.request, ' New Person Added')
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class CreateOccupPage(FormView):
    form_class = CreateOccupForm
    template_name = 'billings/form.html'

    def get_context_data(self, **kwargs):
        context = super(CreateOccupPage, self).get_context_data(**kwargs)

        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'The occupation added!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('billings:payroll_page')


@staff_member_required
def payroll_invoice_paid(request, dk):
    instance = get_object_or_404(PayrollInvoice, id=dk)
    instance.is_paid = True
    instance.save()
    messages.success(request, 'The %s invoice is paid!' % instance.person.title)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@staff_member_required
def payroll_invoice_delete(request, dk):
    instance = get_object_or_404(PayrollInvoice, id=dk)
    instance.delete()
    messages.success(request, 'The %s invoice is deleted!' % instance.person.title)
    return HttpResponseRedirect(reverse('billings:payroll_page'))