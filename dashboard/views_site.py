from django.views.generic import ListView, TemplateView, CreateView, UpdateView, DeleteView
from django.shortcuts import reverse, get_object_or_404, HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from homepage.models import Banner
from point_of_sale.views import Coupons
from homepage.forms import BannerForm


@method_decorator(staff_member_required, name='dispatch')
class SiteView(TemplateView):
    template_name = 'dashboard/site_templates/homepage.html'

    def get_context_data(self, **kwargs):
        context = super(SiteView, self).get_context_data(**kwargs)
        page_title = 'Site Settings'

        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class BannerView(ListView):
    model = Banner
    template_name = 'dashboard/site_templates/banners.html'


@method_decorator(staff_member_required, name='dispatch')
class BannerCreateView(CreateView):
    model = Banner
    form_class = BannerForm
    template_name = 'dashboard/form_view.html'

    def get_context_data(self, **kwargs):
        context = super(BannerCreateView, self).get_context_data(**kwargs)
        page_title, back_url = 'Create Banner', self.get_success_url()
        context.update(locals())
        return context

    def get_success_url(self):
        return reverse('dashboard:banner_view')


@method_decorator(staff_member_required, name='dispatch')
class BannerEditView(UpdateView):
    model = Banner
    form_class = BannerForm
    template_name = 'dashboard/form_view.html'

    def get_success_url(self):
        return reverse('dashboard:banner_view')


@staff_member_required
def banner_delete(request, pk):
    instance = get_object_or_404(Banner, id=pk)
    instance.delete()
    return HttpResponseRedirect(reverse('dashboard:banner_view'))


@method_decorator(staff_member_required, name='dispatch')
class CouponsView(ListView):
    model = Coupons
    template_name = 'dashboard/site_templates/coupons.html'


@method_decorator(staff_member_required, name='dispatch')
class CouponCreate(CreateView):
    model = Coupons
    form_class = ''
    template_name = ''
    success_url = reverse_lazy('dashboard:coupons_view')