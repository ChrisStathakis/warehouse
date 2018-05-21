from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect, HttpResponseRedirect
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, FormView, View
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Q, Sum
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.forms import formset_factory, inlineformset_factory

from .tools import dashboard_product_get_filter_data ,dashboard_product_filter_queryset
from products.models import *
from products.forms import *
from point_of_sale.models import *
from transcations.models import *
from .forms import (UpdateProductForm, CreateProductForm,
                    CategorySiteForm, BrandsForm,
                    ColorForm, SizeForm,
                    CategorySiteForm,
                    )
from products.forms_popup import ProductPhotoUploadForm
from products.forms import SizeAttributeForm, ProductPhotoFormSet
from dateutil.relativedelta import relativedelta


@method_decorator(staff_member_required, name='dispatch')
class DashBoard(TemplateView):
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(DashBoard, self).get_context_data(**kwargs)
        new_orders = RetailOrder.objects.filter(status='1')
        eshop_orders = new_orders.filter(order_type='e')
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class ProductsList(ListView):
    template_name = 'dashboard/products_list.html'
    model = Product
    paginate_by = 50

    def get_queryset(self):
        queryset = Product.objects.all()
        queryset = dashboard_product_filter_queryset(self.request, queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ProductsList, self).get_context_data(**kwargs)
        categories, vendors, colors, brands, site_categories = Category.objects.all(), Supply.objects.all(), \
                                                               Color.objects.all(), Brands.objects.all(), \
                                                               CategorySite.objects.all()
        # get filters data
        search_name, category_name, brand_name, active_name, color_name, vendor_name, \
        site_cate_name, order_name = dashboard_product_get_filter_data(self.request)
        products, currency = True, CURRENCY
        page_title = 'Product list'
        context.update(locals())
        return context

    def post(self, *args, **kwargs):
        get_products = self.request.POST.getlist('choice_name', None)
        new_brand = get_object_or_404(Brands, id=self.request.POST.get('change_brand')) \
            if self.request.POST.get('change_brand') else None
        new_category = get_object_or_404(Category, id=self.request.POST.get('change_cate')) \
            if self.request.POST.get('change_cate') else None
        new_cate_site = get_object_or_404(CategorySite, id=self.request.POST.get('change_cate_site')) \
            if self.request.POST.get('change_cate_site') else None
        new_vendor = get_object_or_404(Supply, id=self.request.POST.get('change_vendor')) \
            if self.request.POST.get('change_vendor') else None
        print(new_cate_site)
        if new_brand and get_products:
            for product_id in get_products:
                product = get_object_or_404(Product, id=product_id)
                print(product_id, product)
                product.brand = new_brand
                product.save()
            messages.success(self.request, 'The brand %s added on the products' % new_brand.title)
            return redirect('dashboard:products')
        if new_category and get_products:
            for product_id in get_products:
                print('new category')
                product = get_object_or_404(Product, id=product_id)
                product.category = new_category
                product.save()
            messages.success(self.request, 'The brand %s added on the products' % new_category.title)
            return redirect('dashboard:products')
        if new_cate_site and get_products:
            print('wtf')
            for product_id in get_products:
                product = get_object_or_404(Product, id=product_id)
                product.category_site.add(new_cate_site)
                product.save()
            messages.success(self.request, 'The category %s added in the products' % new_cate_site.title)

        if new_vendor:
            queryset = Product.objects.all()
            queryset = dashboard_product_filter_queryset(self.request, queryset)
            queryset.update(supply=new_vendor)
            messages.success(self.request, 'The Vendor Updated!')
        return render(self.request, self.template_name)


@staff_member_required
def product_detail(request, pk):
    instance = get_object_or_404(Product, id=pk)
    products, currency, page_title = True, CURRENCY, '%s' % instance.title
    images = instance.get_all_images()
    sizes = SizeAttribute.objects.filter(product_related=instance) if instance.size else None
    chars = ProductCharacteristics.objects.filter(product_related=instance)
    related_products = RelatedProducts.objects.filter(title=instance)
    diff_color = SameColorProducts.objects.filter(title=instance)
    form = UpdateProductForm(request.POST or None, instance=instance)
    SizeAttrFormSet = formset_factory(SizeAttributeForm)
    if sizes:
        formset_size = SizeAttrFormSet(initial=[
                                            {'qty': ele.qty, 'title': ele.title, 'product_related': ele.product_related} for ele in sizes
                                            ])
    if 'size_' in request.POST:
        if sizes:
            formset_size = SizeAttrFormSet(request.POST, initial=[
                                            {'qty': ele.qty, 'title': ele.title, 'product_related': ele.product_related} for ele in sizes
                                            ])
        else:
            formset_size = SizeAttributeForm(request.POST)
        for form in formset_size:
            if form.is_valid():
                try:
                    product = SizeAttribute.objects.get(title=form.cleaned_data['title'],
                                                        product_related=form.cleaned_data['product_related']
                                                        )
                    product.qty = form.cleaned_data['qty']
                    product.save()
                except:
                    form.save()
        return redirect(reverse('dashboard:product_detail', kwargs={'pk': instance.id}))
    if 'save_' in request.POST:
        if form.is_valid():
            form.save()
            messages.success(request, 'The products %s is saves!')
            return HttpResponseRedirect(reverse('dashboard:products'))
    if 'update_' in request.POST:
        form.save()
        messages.success(request, 'The products %s is edited!')
        return HttpResponseRedirect(reverse('dashboard:product_detail', kwargs={'pk': pk}))
    context = locals()
    return render(request, 'dashboard/product_detail.html', context)


@method_decorator(staff_member_required, name='dispatch')
class ProductAddMultipleImages(View):
    template_name = 'dashboard/form_set.html'

    def get(self, request, dk):
        instance = get_object_or_404(Product, id=dk)
        photos = ProductPhotos.objects.filter(product=instance)
        form = ProductPhotoForm()
        return render(request, self.template_name, context=locals())

    def post(self, request, dk):
        data = {}
        instance = get_object_or_404(Product, id=dk)
        form = ProductPhotoUploadForm()
        if request.POST:
            form = ProductPhotoUploadForm(request.POST, request.FILES)
            if form.is_valid():
                photo = ProductPhotos.objects.create(product=instance,
                                                     image=form.cleaned_data.get('image')
                                                     )
                data = {'is_valid': True,
                        'name': photo.product.title,
                        'url': photo.image.url
                        }
        data['html_data'] = render_to_string(request=request,
                                             template_name='dashboard/ajax_calls/images.html',
                                             context={'photos': ProductPhotos.objects.filter(product=instance) }   
                                            )
        print(data)
        return JsonResponse(data)


@staff_member_required
def delete_product_image(request, pk):
    instance = get_object_or_404(ProductPhotos, id=pk)
    instance.delete()
    messages.success(request, 'The image has deleted')
    return HttpResponseRedirect(reverse('dashboard:product_detail', kwargs={'pk': instance.product.id}))


@staff_member_required
def product_add_sizechart(request, dk):
    instance = get_object_or_404(Product, id=dk)
    sizes_attr = instance.sizeattribute_set.all()
    sizes = Size.objects.filter(status=True)
    return render(request, 'dashboard/size_chart.html', context=locals())


@method_decorator(staff_member_required, name='dispatch')
class RelatedProductsView(ListView):
    model = Product
    template_name = 'dashboard/product_related_products.html'

    def get_queryset(self):
        queryset = Product.my_query.active_for_site()

        return queryset

    def get_context_data(self, pk,  **kwargs):
        context = super(RelatedProductsView, self).get_context_data(**kwargs)
        instance = get_object_or_404(Product, id=pk)
        context.update(locals())
        return context


@staff_member_required
def create_new_sizechart(request, dk, pk):
    data = dict()
    instance = get_object_or_404(Product, id=dk)
    size = get_object_or_404(Size, id=pk)
    size_exists = SizeAttribute.objects.filter(title=size, product_related=instance)
    if size_exists:
        data['new_'] = False
        sizes_attr = SizeAttribute.objects.filter(product_related=instance)
    else:
        data['new'] = True
        new_size = SizeAttribute.objects.create(title=size,
                                                product_related=instance
                                                )
        sizes_attr = SizeAttribute.objects.filter(product_related=instance)
    data['html_data'] = render_to_string(request=request, template_name='dashboard/ajax_calls/sizeattr.html', context=locals())

    return JsonResponse(data)


@staff_member_required
def create_copy_item(request, pk):
    object = get_object_or_404(Product, id=pk)
    object.id = None
    object.slug = None
    object.save()
    return redirect(object.get_edit_url())


@method_decorator(staff_member_required, name='dispatch')
class ProductCreate(CreateView):
    template_name = 'dashboard/product_create.html'
    form_class = CreateProductForm
    new_object = None

    def get_context_data(self, **kwargs):
        context = super(ProductCreate, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        object = form.save()
        object.refresh_from_db()
        self.new_object = object
        return super().form_valid(form)

    def get_success_url(self):
        self.new_object.refresh_from_db()
        return reverse('dashboard:product_detail', kwargs={'pk': self.new_object.id})


@staff_member_required
def delete_product(request, dk):
    instance = get_object_or_404(Product, id=dk)
    instance.delete()
    return HttpResponseRedirect(reverse('dashboard:products'))


@method_decorator(staff_member_required, name='dispatch')
class CategorySitePage(ListView):
    template_name = 'dashboard/category_site_list.html'
    model = CategorySite
    paginate_by = 50

    def get_queryset(self):
        queryset = CategorySite.objects.all()
        search_name = self.request.GET.get('search_name', None)
        active_name = self.request.GET.get('active_name', None)
        queryset = CategorySite.filter_data(queryset, search_name, active_name)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(CategorySitePage, self).get_context_data(**kwargs)
        search_name = self.request.GET.get('search_name', None)
        active_name = self.request.GET.get('active_name', None)
        page_title = 'Site Categories'
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class CategoryPage(ListView):
    template_name = 'dashboard/page_list.html'
    model = Category
    paginate_by = 50

    def get_queryset(self):
        queryset = Category.objects.all()
        active_name, show_name, search_name = [self.request.GET.getlist('active_name'),
                                               self.request.GET.getlist('show_name'),
                                               self.request.GET.get('search_name')
                                               ]
        queryset = queryset.filter(title__icontains=search_name) if search_name else queryset
        queryset = queryset.filter(active=True) if active_name == ['1'] else queryset.filter(active=False) \
            if active_name == ['2'] else queryset
        return queryset

    def get_context_data(self, **kwargs):
        context = super(CategoryPage, self).get_context_data(**kwargs)
        title, create_title, create_url, category_page = 'Categories', 'Create Category', reverse('dashboard:category_create', kwargs={}), True
        table_thead = ['id', 'Name', 'Active', 'Main Page', 'Parent']
        active_name, show_name, search_name = [self.request.GET.getlist('active_name'),
                                               self.request.GET.getlist('show_name'),
                                               self.request.GET.get('search_name')
                                               ]
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class BrandPage(ListView):
    template_name = 'dashboard/brand_list.html'
    model = Brands
    paginate_by = 50

    def get_queryset(self):
        queryset = Brands.objects.all()
        search_name = self.request.GET.get('search_name', None)
        active_name = self.request.GET.get('active_name', None)
        queryset = Brands.filters_data(queryset, search_name, active_name)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(BrandPage, self).get_context_data(**kwargs)
        title, create_title, create_url = 'Brands', 'Create Brand', ''
        search_name = self.request.GET.get('search_name', None)
        active_name = self.request.GET.get('active_name', None)
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class ColorPage(ListView):
    template_name = 'dashboard/color_list.html'
    model = Color
    paginate_by = 50

    def get_queryset(self):
        queryset = Color.objects.all()
        search_name = self.request.GET.get('search_name', None)
        active_name = self.request.GET.get('active_name', None)
        queryset = Color.filters_data(queryset, search_name, active_name)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ColorPage, self).get_context_data(**kwargs)
        page_title, create_title, create_url = 'Colors', 'Create Color', reverse('dashboard:color_create')
        table_thead = ['id', 'Name', 'Active']
        search_name = self.request.GET.get('search_name', None)
        active_name = self.request.GET.get('active_name', None)
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class SizePage(ListView):
    template_name = 'dashboard/size_list.html'
    model = Size
    paginate_by = 50

    def get_queryset(self):
        queryset = Size.objects.all()
        search_name = self.request.GET.get('search_name', None)
        active_name = self.request.GET.get('active_name', None)
        queryset = Size.filters_data(queryset, search_name, active_name)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(SizePage, self).get_context_data(**kwargs)
        search_name = self.request.GET.get('search_name', None)
        active_name = self.request.GET.get('active_name', None)
        page_title = 'Sizes'
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class CategoryDetail(UpdateView):
    template_name = 'dashboard/page_detail.html'
    model = CategorySite
    form_class = CategorySiteForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CategoryDetail, self).get_context_data(**kwargs)
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class CategoryCreate(CreateView):
    template_name = 'dashboard/page_create.html'
    form_class = CategorySiteForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CategoryCreate, self).get_context_data(**kwargs)
        title = 'Create Category'
        context.update(locals())
        return context

    def get_success_url(self):
        return reverse('dashboard:categories')


@method_decorator(staff_member_required, name='dispatch')
class CategorySiteCreate(CreateView):
    model = CategorySite
    template_name = 'dashboard/page_create.html'
    form_class = CategorySiteForm

    def get_context_data(self, **kwargs):
        context = super(CategorySiteCreate, self).get_context_data(**kwargs)
        title = 'Create New Site Category'
        context.update(locals())
        return context

    def get_success_url(self):
        return reverse('dashboard:categories_site')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'New category added!')
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class BrandsCreate(CreateView):
    form_class = BrandsForm
    template_name = 'dashboard/form_view.html'

    def get_context_data(self, **kwargs):
        context = super(BrandsCreate, self).get_context_data(**kwargs)
        title = 'Create Brand'
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'The Brand Created!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboard:brands')


@method_decorator(staff_member_required, name='dispatch')
class ColorCreate(CreateView):
    model = Color
    form_class = ColorForm
    template_name = 'dashboard/page_create.html'

    def get_context_data(self, **kwargs):
        context = super(ColorCreate, self).get_context_data(**kwargs)
        title = 'Create Color'
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'The color Created!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboard:colors')


@method_decorator(staff_member_required, name='dispatch')
class ColorEditPage(UpdateView):
    model = Color
    form_class = ColorForm
    template_name = 'dashboard/form_view.html'

    def get_context_data(self, **kwargs):
        context = super(ColorEditPage, self).get_context_data(**kwargs)
        page_title, back_url = 'Edit Color', reverse('dashboard:colors')
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Th color edited!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboard:colors')


@method_decorator(staff_member_required, name='dispatch')
class SizeCreate(CreateView):
    model = Size
    form_class = SizeForm
    template_name = 'dash_ware/form.html'

    def get_context_data(self, **kwargs):
        context = super(SizeCreate, self).get_context_data(**kwargs)
        page_title = form_title = 'Create Size'
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'The Brand Created!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboard:sizes')


@staff_member_required
def brandEditPage(request, pk):
    instance = get_object_or_404(Brands, id=pk)
    form_title = instance.title
    form = BrandForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('dashboard:brands'))
    context = locals()
    return render(request, 'dashboard/form_view.html', context)


@method_decorator(staff_member_required, name='dispatch')
class SizeEditPage(FormView):
    form_class = SizeForm
    template_name = 'dashboard/form_view.html'

    def get_context_data(self, **kwargs):
        context = super(SizeEditPage, self).get_context_data(**kwargs)
        page_title = form_title = 'Edit Size'
        context.update(locals())
        return context

    def get_success_url(self):
        return reverse('dashboard:sizes')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'The size had edited')
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class CategorySiteEdit(UpdateView):
    model = CategorySite
    form_class = CategorySiteForm
    template_name = 'dashboard/page_create.html'

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'The category edited successfuly!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboard:categories_site')


@staff_member_required
def category_site_edit(request, dk):
    instance = get_object_or_404(CategorySite, id=dk)
    form = CategorySiteForm(request.POST or None, instance=instance)
    form_title = page_title = 'Edit %s' % instance.title
    if form.is_valid():
        form.save()
        messages.success(request, 'The category %s edited successfully' % instance.title)
    context = locals()
    return render(request, 'dashboard/form_view.html', context)


@staff_member_required
def delete_category(request, pk):
    category = get_object_or_404(CategorySite, id=pk)
    category.delete()
    messages.warning(request, 'The category has deleted')
    return redirect(reverse('dashboard:categories'))


@staff_member_required
def delete_brand(request, pk):
    instance = get_object_or_404(Brands, id=pk)
    instance.delete()
    messages.warning(request, 'The brand %s has deleted' % instance.title)
    return redirect(reverse('dashboard:brands'))


@staff_member_required
def delete_color(request, pk):
    instance = get_object_or_404(Color, id=pk)
    instance.delete()
    messages.warning(request, 'The color %s deleted' % instance.title)
    return redirect(reverse('dashboard:colors'))
