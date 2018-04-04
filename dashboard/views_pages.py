from django.views.generic import View
from django.shortcuts import render, HttpResponseRedirect, reverse, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from homepage.models import FirstPage, Banner
from homepage.forms import BannerForm, FirstPageForm


@method_decorator(staff_member_required, name='dispatch')
class PageConfigView(View):
    template_name = 'dashboard/page_config/index.html'

    def get(self, request):
        banners = Banner.objects.all()
        first_pages = FirstPage.objects.all()
        context = locals()
        return render(request, self.template_name, context)


@staff_member_required
def create_banner(request):
    form_title = 'Create Banner'
    form = BannerForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'New Banner added in gallery')
        return HttpResponseRedirect(reverse('dashboard:page_config'))
    context = locals()
    return render(request, 'dashboard/page_config/form_page.html', context)


@staff_member_required
def edit_banner_page(request, dk):
    instance = get_object_or_404(Banner, id=dk)
    form_title = 'Edit %s' % instance.title
    form = BannerForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        messages.success(request, 'The banner edited!')
        return HttpResponseRedirect(reverse('dashboard:page_config'))
    context = locals()
    return render(request, 'dashboard/page_config/form_page.html', context)


@staff_member_required
def delete_banner(request, dk):
    banner = get_object_or_404(Banner, id=dk)
    banner.delete()
    return HttpResponseRedirect(reverse('dashboard:page_config'))


@staff_member_required
def create_first_page(request):
    form_title = 'Create Banner'
    form = FirstPageForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'New Page added in gallery')
        return HttpResponseRedirect(reverse('dashboard:page_config'))
    context = locals()
    return render(request, 'dashboard/page_config/form_page.html', context)


@staff_member_required
def edit_first_page(request, dk):
    instance = get_object_or_404(FirstPage, id=dk)
    form_title = 'Edit %s' % instance.title
    form = FirstPageForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        messages.success(request, 'The banner edited!')
        return HttpResponseRedirect(reverse('dashboard:page_config'))
    context = locals()
    return render(request, 'dashboard/page_config/form_page.html', context)


@staff_member_required
def delete_first_page(request, dk):
    get_object = get_object_or_404(FirstPage, id=dk)
    get_object.delete()
    return HttpResponseRedirect(reverse('dashboard:page_config'))