from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect, HttpResponseRedirect
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView
from django.db.models import Q, Sum
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages

from .tools import dashboard_product_get_filter_data ,dashboard_product_filter_queryset
from products.models import *
from products.forms import *
from point_of_sale.models import *
from transcations.models import *
from .forms import UpdateProductForm, CreateProductForm, CategorySiteForm, BrandsForm, ColorForm, SizeForm

from dateutil.relativedelta import relativedelta


@method_decorator(staff_member_required, name='dispatch')
class DashBoard(TemplateView):
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(DashBoard, self).get_context_data(**kwargs)
        new_orders = RetailOrder.objects.filter(status='1')
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
        search_name, category_name, brand_name, active_name, color_name, vendor_name, order_name = dashboard_product_get_filter_data(self.request)
        products, currency = True, CURRENCY
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
        return render(self.request, self.template_name)


@staff_member_required()
def product_detail(request, pk):
    products, currency = True, CURRENCY
    instance = get_object_or_404(Product, id=pk)
    images = instance.get_all_images()
    print(images)
    chars = ProductCharacteristics.objects.filter(product_related=instance)
    related_products = RelatedProducts.objects.filter(title=instance)
    
    form = UpdateProductForm(request.POST or None, instance=instance)
    form_image = ProductPhotoForm(request.POST or None,
                                  request.FILES or None,
                                  initial={'product': instance,}
                                  )
    if form_image.is_valid():
        form_image.save()
        return HttpResponseRedirect(reverse('dashboard:products'))
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('dashboard:products'))
    context = locals()
    return render(request, 'dashboard/product_detail.html', context)


def create_copy_item(request, pk):
    object = get_object_or_404(Product, id=pk)
    object.id = None
    object.save()
    return redirect(object.get_edit_url())


@method_decorator(staff_member_required, name='dispatch')
class ProductCreate(CreateView):
    template_name = 'dashboard/product_create.html'
    form_class = CreateProductForm

    def get_context_data(self, **kwargs):
        context = super(ProductCreate, self).get_context_data(**kwargs)

        return context

    def form_valid(self, form):
        object = form.save()
        return redirect(object.get_edit_url())

    def get_success_url(self):
        return reverse('dashboard:product_detail', kwarg={'dk': Product.objects.last()})


@staff_member_required
def delete_product(request, dk):
    instance = get_object_or_404(Product, id=dk)
    instance.delete()
    return HttpResponseRedirect(reverse('dashboard:products'))


@method_decorator(staff_member_required, name='dispatch')
class CategoryPage(ListView):
    template_name = 'dashboard/page_list.html'
    model = CategorySite

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        queryset = CategorySite.objects.all()
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

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(BrandPage, self).get_context_data(**kwargs)
        title, create_title, create_url = 'Brands', 'Create Brand', ''
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class ColorPage(ListView):
    template_name = 'dashboard/page_list.html'
    model = Color

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ColorPage, self).get_context_data(**kwargs)
        title, create_title, create_url = 'Brands', 'Create Brand', ''
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class SizePage(ListView):
    template_name = 'dashboard/page_list.html'
    model = Size

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SizePage, self).get_context_data(**kwargs)
        title, create_title, create_url = 'Size', 'Create Size', ''
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
class BrandsCreate(CreateView):
    form_class = BrandsForm
    template_name = 'dashboard/page_create.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(BrandsCreate, self).get_context_data(**kwargs)
        title = 'Create Brand'
        context.update(locals())
        return context

    def form_valid(self, form):
        messages.success(self.request, 'The Brand Created!')
        return reverse('dashboard:brands')


@method_decorator(staff_member_required, name='dispatch')
class ColorCreate(CreateView):
    form_class = ColorForm
    template_name = 'dashboard/page_create.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ColorCreate, self).get_context_data(**kwargs)
        title = 'Create Color'
        context.update(locals())
        return context

    def form_valid(self, form):
        messages.success(self.request, 'The color Created!')
        return reverse('dashboard:brands')


@method_decorator(staff_member_required, name='dispatch')
class SizeCreate(CreateView):
    form_class = BrandsForm
    template_name = 'dashboard/page_create.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SizeCreate, self).get_context_data(**kwargs)
        title = 'Create Size'
        context.update(locals())
        return context

    def form_valid(self, form):
        messages.success(self.request, 'The Brand Created!')
        return reverse('dashboard:brands')


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
