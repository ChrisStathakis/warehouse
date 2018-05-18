from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import Sum
from django.utils.translation import pgettext_lazy
from django.conf import settings
from mptt.models import MPTTModel, TreeForeignKey
from tinymce.models import HTMLField


import os
from time import time
import datetime
from decimal import Decimal
from dashboard.constants import *
from dashboard.models import PaymentOrders
# Create your models here.



MEDIAURL = 'media'
#MEDIAURL = 'https://monastiraki.s3.amazonaws.com/media/'


def product_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'product/{0}/{1}'.format(instance.product.title, filename)


def category_site_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'category_site/{0}/{1}'.format(instance.title, filename)


def upload_location(instance, filename):
    return "%s%s" %(instance.id, filename)


def my_awesome_upload_function(instance, filename):
    """ this function has to return the location to upload the file """
    return os.path.join('/media_cdn/%s/' % instance.id, filename)


class CategorySiteManager(models.Manager):
    def main_page_show(self):
        return super(CategorySiteManager, self).filter(status='a', parent__isnull=True)


class CategorySite(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=120)
    image = models.ImageField(blank=True, null=True, upload_to=category_site_directory_path, help_text='610*410')
    content = models.TextField(blank=True, null=True)
    date_added = models.DateField(auto_now=True)
    meta_description = models.CharField(max_length=300, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)
    order = models.IntegerField(default=1)
    slug = models.SlugField(blank=True, null=True, allow_unicode=True)
    show_on_menu = models.BooleanField(default=False, verbose_name='Active on Navbar')
    my_query = CategorySiteManager()
    objects = models.Manager()

    class Meta:
        verbose_name_plural = '3. Κατηγορίες Site'
        unique_together = (('slug', 'parent',))
        ordering = ['-order', ]

    def __str__(self):
        full_path = [self.title]
        k = self.parent
        while k is not None:
            full_path.append(k.title)
            k = k.parent
        return ' -> '.join(full_path[::-1])

    def image_tag(self):
        if self.image:
            return mark_safe('<img scr="%s%s" width="400px" height="400px" />'%(MEDIAURL, self.image))

    def image_tag_tiny(self):
        if self.image:
            return mark_safe('<img scr="%s%s" width="100px" height="100px" />'%(MEDIAURL, self.image))
    image_tag.short_description = 'Είκονα'

    def get_edit_url(self):
        return reverse('dashboard:category_detail', kwargs={'pk': self.id})

    def get_absolute_url(self):
        return reverse('dashboard:categories')

    def absolute_url_site(self):
        pass

    def get_childrens(self):
        childrens = CategorySite.objects.filter(parent=self)
        return childrens
    
    @staticmethod
    def filter_data(queryset, search_name, active_name):
        queryset = queryset.filter(title__icontains=search_name) if search_name else queryset
        queryset = queryset.filter(active=True) if active_name else queryset
        return queryset


class Brands(models.Model):
    active = models.BooleanField(default=True, verbose_name='Ενεργοποίηση')
    title = models.CharField(max_length=120, verbose_name='Ονομασία Brand')
    image = models.ImageField(blank=True, upload_to='brands/', verbose_name='Εικόνα')
    order_by = models.IntegerField(default=1,verbose_name='Σειρά Προτεριότητας')
    meta_description =models.CharField(max_length=255, blank=True)
    width = models.IntegerField(default=240)
    height = models.IntegerField(default=240)
    slug = models.SlugField(blank=True, null=True, allow_unicode=True)

    class Meta:
        verbose_name_plural = '4. Brands'
        ordering = ['-title']

    def __str__(self):
        return self.title

    def image_tag(self):
        return mark_safe('<img scr="%s/%s" width="400px" height="400px" />'%(MEDIAURL, self.image))

    def image_tag_tiny(self):
        return mark_safe('<img scr="%s/%s" width="100px" height="100px" />'%(MEDIAURL, self.image))
    image_tag.short_description = 'Είκονα'

    def get_absolute_url(self):
        return reverse('brand', kwargs={'slug': self.slug})

    @staticmethod
    def filters_data(queryset, search_name, active_name):
        queryset = queryset.filter(title__icontains=search_name) if search_name else queryset
        queryset = queryset.filter(active=True) if active_name else queryset
        return queryset


class Characteristics(models.Model):
    title = models.CharField(max_length=60,)

    def __str__(self):
        return self.title


class Category(models.Model):
    title = models.CharField(unique=True,max_length=70,verbose_name='Τίτλος Κατηγορίας')
    description = models.TextField(null=True,blank=True, verbose_name='Περιγραφή')

    class Meta:
        ordering = ['title']
        verbose_name = "3. Κατηγορίες Αποθήκης"
        verbose_name_plural = '3. Κατηγορίες Αποθήκης'

    def __str__(self):
        return self.title


class TaxesCity(models.Model):
    title = models.CharField(max_length=64,unique=True)

    class Meta:
        verbose_name="ΔΟΥ   "

    def __str__(self):
        return self.title


class Supply(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(unique=True, max_length=70, verbose_name="'Ονομα")
    afm = models.CharField(max_length=9, blank=True, null=True, verbose_name="ΑΦΜ")
    doy = models.ForeignKey(TaxesCity, verbose_name='Εφορία', null=True, blank=True, on_delete=models.CASCADE)
    phone = models.CharField(max_length=10, null=True, blank=True, verbose_name="Τηλέφωνο")
    phone1 = models.CharField(max_length=10, null=True, blank=True, verbose_name="Τηλέφωνο")
    fax = models.CharField(max_length=10, null=True, blank=True, verbose_name="Fax")
    email = models.EmailField(null=True, blank=True, verbose_name="Email")

    site = models.CharField(max_length=40, blank=True, null=True, verbose_name='Site')
    address = models.CharField(max_length=40, null=True, blank=True, verbose_name='Διεύθυνση')
    city = models.CharField(max_length=40, null=True, blank=True, verbose_name='Πόλη')
    zip_code = models.CharField(max_length=40, null=True, blank=True, verbose_name='TK')
    description = models.TextField(null=True, blank=True, verbose_name="Περιγραφή")
    date_added = models.DateField(default=timezone.now)
    taxes_modifier = models.CharField(max_length=1, choices=TAXES_CHOICES, default='3')
    # managing deposits
    remaining_deposit = models.DecimalField(default=0, decimal_places=2, max_digits=100,
                                            verbose_name='Υπόλοιπο προκαταβολών')
    balance = models.DecimalField(default=0, max_digits=100, decimal_places=2, verbose_name="Υπόλοιπο")
    payment_orders = GenericRelation(PaymentOrders)

    class Meta:
        verbose_name_plural = '9. Προμηθευτές'
        ordering = ['title', ]
        
    def save(self, *args, **kwargs):
        orders = self.order_set.all()
        self.balance = orders.aggregate(Sum('total_price'))['total_price__sum'] if orders else 0
        self.balance -= orders.aggregate(Sum('paid_value'))['paid_value__sum'] if orders else 0
        self.balance -= self.payment_orders.filter(is_paid=True).aggregate(Sum('value'))['value__sum'] \
        if self.payment_orders.filter(is_paid=True) else 0
        self.remaining_deposit = self.payment_orders.filter(is_paid=False).aggregate(Sum('value'))['value__sum'] \
        if self.payment_orders.filter(is_paid=False) else 0
        super(Supply, self).save(*args, **kwargs)

    @staticmethod
    def filter_data(request, queryset):
        search_name = request.GET.get('search_name', None)
        vendor_name = request.GET.getlist('vendor_name', None)
        balance_name = request.GET.get('balance_name', None)
        try:
            queryset = queryset.filter(title__icontains=search_name) if search_name else queryset
            queryset = queryset.filter(balance__gte=1) if balance_name else queryset
            queryset = queryset.filter(id__in=vendor_name) if vendor_name else queryset
        except:
            queryset = queryset
        return queryset

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('reports:vendor_detail', args={'dk': self.id})

    def template_tag_remaining_deposit(self):
        return ("{0:.2f}".format(round(self.remaining_deposit, 2))) + ' %s'%(CURRENCY)

    def tag_balance(self):
        return ("{0:.2f}".format(round(self.balance, 2))) + ' %s'%(CURRENCY)

    def tag_deposit(self):
        return "%s %s" % (self.remaining_deposit, CURRENCY)

    def tag_phones(self):
        return '%s' % self.phone if self.phone else ' ' + ', %s' % self.phone1 if self.phone1 else ' '     

    def get_absolute_url_form(self):
        return reverse('edit_vendor_id',kwargs={'dk':self.id})


class Color(models.Model):
    title = models.CharField(max_length=64, unique=True, verbose_name='Ονομασία Χρώματος')
    status = models.BooleanField(default=True, verbose_name='Κατάσταση')
    code_id = models.CharField(max_length=25, blank=True, verbose_name='Κωδικός Χρώματος')
    ordering = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name_plural = '5. Χρώματα'
        ordering = ['-ordering', ]

    def __str__(self):
        return self.title

    def tag_status(self):
        return 'Active' if self.status else 'No Active'

    @staticmethod
    def filters_data(queryset, search_name, active_name):
        queryset = queryset.filter(title__icontains=search_name) if search_name else queryset
        queryset = queryset.filter(status=True) if active_name else queryset
        return queryset


class Size(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=64, unique=True, verbose_name='Ονομασία Μεγέθους')
    status = models.BooleanField(default=True, verbose_name='Κατάσταση')
    ordering = models.PositiveIntegerField(default=1, help_text='Bigger goes first')

    class Meta:
        verbose_name_plural = '6. Μεγέθη'
        ordering = ['-ordering', ]

    def __str__(self):
        return self.title

    def get_edit_url(self):
        return reverse('dashboard:edit_size', kwargs={'pk': self.id})

    @staticmethod
    def filters_data(queryset, search_name, active_name):
        queryset = queryset.filter(title__icontains=search_name) if search_name else queryset
        queryset = queryset.filter(status=True) if active_name else queryset
        return queryset


class ProductManager(models.Manager):
    def active_warehouse(self):
        return super(ProductManager, self).filter(active=True)

    def active_for_site(self):
        return self.active_warehouse().filter(site_active=True)

    def active_with_qty(self):
        return self.active_warehouse().filter(qty__gte=1)

    def first_page_new_products(self):
        return self.active_with_qty().order_by('-id')[0:16]

    def first_page_offers(self):
        return self.active_with_qty().filter(is_offer=True)[0:16]

    def first_page_featured_products(self):
        return self.active_with_qty().filter(is_featured=True)

    def active_with_brand(self, brand):
        return super(ProductManager, self).filter(brand__id=brand, ware_active=True, status=True)

    def active_category_site(self, categories):
        return self.active_for_site().filter(category_site__in=categories)

    def active_get_all_category_site(self, list_of_category):
        return super(ProductManager, self).filter(ware_active=True, status= True, qty__gte=1, category_site__in=list_of_category)

    def active_get_one_category_site(self, category):
        return super(ProductManager, self).filter(ware_active=True, status=True, category_site=category)

    def site_offers(self):
        return super(ProductManager, self).filter(price_discount__gte=0.01, ware_active=True, status=True, qty__gte=1)


class Product(models.Model):
    active = models.BooleanField(default=True, verbose_name='Active')
    site_active = models.BooleanField(default=True, verbose_name='Active for Site')
    wholesale_active = models.BooleanField(default=False, verbose_name="Active for WholeSale")
    is_service = models.BooleanField(default=False, verbose_name='Service')
    is_featured = models.BooleanField(default=True, verbose_name='Featured Product')
    is_offer = models.BooleanField(default=True)
    size = models.BooleanField(default=False, verbose_name='Μεγεθολόγιο')
    title = models.CharField(max_length=120, verbose_name="'Ονομα προιόντος")
    color = models.ForeignKey(Color, blank=True, null=True, verbose_name='Χρώμα', on_delete=models.CASCADE)
    #  warehouse data
    order_code = models.CharField(null=True, blank=True, max_length=100, verbose_name="Κωδικός Τιμολογίου")
    price_buy = models.DecimalField(decimal_places=2, max_digits=6, default=0, verbose_name="Τιμή Αγοράς") # the price which you buy the product
    order_discount = models.IntegerField(default=0, verbose_name="'Εκπτωση Τιμολογίου σε %")
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.SET_NULL)
    supply = models.ForeignKey(Supply, verbose_name="Προμηθευτής", blank=True, null=True, on_delete=models.SET_NULL)

    qty_kilo = models.DecimalField(max_digits=5, decimal_places=3, default=1, verbose_name='Βάρος/Τεμάχια ανά Συσκευασία ')
    qty = models.DecimalField(default=0, verbose_name="Απόθεμα", max_digits=10, decimal_places=2)
    barcode = models.CharField(max_length=6, null=True, blank=True, verbose_name='Κωδικός/Barcode')
    notes = models.TextField(null=True, blank=True, verbose_name='Περιγραφή')
    measure_unit = models.CharField(max_length=1, default='1', choices=UNIT, blank=True, null=True)
    safe_stock = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    objects = models.Manager()
    my_query = ProductManager()

    #site attritubes
    sku = models.CharField(max_length=150, blank=True, null=True)
    site_text = HTMLField(blank=True, null=True)
    meta_description = models.CharField(max_length=300, null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS_SITE, default='1')
    category_site = models.ManyToManyField(CategorySite, blank=True, null=True)
    brand = models.ForeignKey(Brands, blank=True, null=True, verbose_name='Brand Name', on_delete=models.SET_NULL)
    slug = models.SlugField(blank=True, null=True, allow_unicode=True)

    # price sell and discount sells
    price = models.DecimalField(decimal_places=2, max_digits=6, default=0, verbose_name="Τιμή λιανικής") #the price product have in the store
    margin = models.IntegerField(default=30, verbose_name='Margin', blank=True, null=True)
    markup = models.IntegerField(default=30, verbose_name='Markup', blank=True, null=True)
    price_internet = models.DecimalField(decimal_places=2, max_digits=6, default=0, verbose_name="Τιμή Internet(No use)")
    price_b2b = models.DecimalField(decimal_places=2, max_digits=6, default=0, verbose_name="Τιμή Χονδρικής") #the price product have in the website, if its 0 then website gets the price from store
    price_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Εκπτωτική Τιμή.')
    final_price = models.DecimalField(default=0, decimal_places=2, max_digits=10, blank=True)
    #size and color

    related_products = models.ManyToManyField('self', blank=True)
    different_color = models.ManyToManyField('self', blank=True)

    date_created = models.DateField( default=timezone.now, verbose_name='Ημερομηνία Δημιουργίας')

    class Meta:
        ordering = ['-id']
        verbose_name_plural = "1. Προϊόντα"

    def save(self, *args, **kwargs):
        if self.price:
            self.final_price = self.price_discount if self.price_discount > 0 else self.price
        self.is_offer = True if self.price_discount > 0 else False
        if self.size:
            self.qty = self.sizeattribute_set.all().aggregate(Sum('qty'))['qty__sum'] if self.sizeattribute_set else 0
        if settings.PRODUCT_TRANSCATIONS:
            qty_add = self.orderitem_set.all().aggregate(Sum('qty'))['qty__sum'] if self.orderitem_set.all() else 0
            qty_minus = 0
            queryset_retail_order = self.retailorderitem_set.all().values('order__order_type').annotate(new_qty=Sum('qty')).order_by('new_qty')\
            if self.retailorderitem_set.all() else None
            if queryset_retail_order:
                for item in queryset_retail_order:
                    if item['order__order_type'] in ['r', 'e', 'wr', 'd']:
                        qty_minus += item['new_qty']
                    else:
                        qty_minus -= item['new_qty']
            self.qty = qty_add - qty_minus
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return '%s %s' % (self.title, self.color) if self.color else self.title

    def tag_category(self):
        return self.category.title if self.category else 'No Category'

    def get_supply(self):
        return self.supply.title if self.supply else 'No Supplier'

    def tag_brand(self):
        return self.brand if self.brand else 'Δεν έχει επιλεχτεί Brand'

    @property
    def get_final_price_buy(self):
        return self.price_buy*((100-self.price_discount)/100)

    @property
    def tag_final_price(self):
        return '%s %s' % (self.final_price, CURRENCY)

    @property
    def tag_final_price_buy(self):
        return '%s %s' % (self.get_final_price_buy, CURRENCY)

    def get_absolute_url(self):
        return reverse('product_page', kwargs={'slug': self.slug})

    def get_edit_url(self):
        return reverse('dashboard:product_detail', kwargs={'pk':self.id})

    def absolute_url_edit_product(self):
        return reverse('edit_product', kwargs={'dk': self.id})

    @property
    def tag_price_buy(self):
        return '%s %s' % (self.price_buy, CURRENCY)

    def tag_price_buy_final(self):
        return '%s %s' % (round(self.get_final_price_buy, 2), CURRENCY)

    def tag_price(self):
        return '%s %s' % (self.price, CURRENCY)

    def tag_remain_warehouse_price_buy(self):
        return '%s %s' % (self.price_buy*self.qty, CURRENCY)

    def tag_remain_warehouse_final_price(self):
        return '%s %s' % (self.final_price*self.qty, CURRENCY)

    def tag_qty(self):
        return '%s %s' % (self.qty, self.get_measure_unit_display())

    @property
    def image(self):
        try:
            return ProductPhotos.objects.filter(active=True, product=self, is_primary=True).last().image
        except:
            pass

    @property
    def image_back(self):
        try:
            return ProductPhotos.objects.filter(active=True, product=self, is_back=True).last().image
        except:
            pass

    
    @property
    def sizes(self):
        return SizeAttribute.objects.filter(product_related=self, qty__gte=1)

    def get_all_images(self):
        return ProductPhotos.objects.filter(active=True, product=self)

    def image_tag(self):
        if self.image:
            return mark_safe('<img src="%s%s" class="img-responsive">'%(MEDIAURL, self.image))
        return mark_safe('<img src="%s" class="img-responsive">' % "{% static 'home/no_image.png' %}")

    def image_back_tag(self):
        if self.image_back:
            return mark_safe('<img src="%s%s" width="200px" height="200px">'%(MEDIAURL, self.image_back))

    def image_tag_tiny(self):
        if self.image:
            return mark_safe('<img src="%s%s" width="100px" height="100px">'%(MEDIAURL, self.image))

    def image_back_tag_tiny(self):
        if self.image_back:
            return mark_safe('<img src="%s%s" width="200px" height="200px">'%(MEDIAURL, self.image_back))

    def show_warehouse_remain(self):
        return self.qty * self.qty_kilo

    @property
    def product_characteristics(self):
        instance = self
        return ProductCharacteristics.my_query.filter_by_instance(instance)

    def tag_related_products(self):
        related_products = self.related_products.all()
        if related_products.count()>0:
            return related_products[:3]
        related_products = Product.objects.filter(category_site__in=self.category_site.all())
        if related_products.count() > 0:
            return related_products[:3]
        return Product.objects.all()[:3]

    @staticmethod
    def filters_data(request, queryset):
        search_name = request.GET.get('search_name', None)
        cate_name = request.GET.getlist('cate_name', None)
        site_cate_name = request.GET.getlist('site_cate_name', None)
        brand_name = request.GET.getlist('brand_name', None)
        vendor_name = request.GET.getlist('vendor_name', None)
        color_name = request.GET.getlist('color_name', None)

        queryset = queryset.filter(category__id__in=cate_name) if cate_name else queryset
        queryset = queryset.filter(brand__id__in=brand_name) if brand_name else queryset
        queryset = queryset.filter(supply__id__in=vendor_name) if vendor_name else queryset
        queryset = queryset.filter(category_site__id__in=site_cate_name) if site_cate_name else queryset
        queryset = queryset.filter(color__id__in=color_name) if color_name else queryset
        queryset = queryset.filter(title__icontains=search_name) if search_name else queryset
        return queryset


class CharacteristicsValue(models.Model):
    title = models.CharField(max_length=100)
    # related_to = models.CharField(blank=True,)

    def __str__(self):
        return self.title


class ProductCharManager(models.Manager):
    def filter_by_instance(self, instance):
        content_type = ContentType.objects.get_for_model(instance.__class__)
        obj_id = instance.id
        qs = super(ProductCharManager, self).filter(content_type=content_type, object_id= obj_id)
        return qs


class ProductCharacteristics(models.Model):
    title = models.ForeignKey(Characteristics, on_delete=models.CASCADE)
    description = models.ForeignKey(CharacteristicsValue, on_delete=models.CASCADE)
    product_related = models.ForeignKey(Product, null=True, blank=True, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id',)
    my_query = ProductCharManager()
    objects = models.Manager()
    focus = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = '9. Χαρακτηριστικά Προϊόντος'

    def __str__(self):
        return str('%s - %s' %(self.title, self.description.title))


class RelatedProducts(models.Model):
    title = models.ForeignKey(Product, related_name='titleg', on_delete=models.CASCADE)
    related = models.ManyToManyField(Product, related_name='relatedgproducts')

    class Meta:
        verbose_name_plural='7. Παρόμοια Προϊόντα'

    def __str__(self):
        return self.title.title


class SameColorProducts(models.Model):
    title = models.ForeignKey(Product, related_name='titlef', on_delete=models.CASCADE)
    related = models.ManyToManyField(Product, related_name='relatedfproducts')

    class Meta:
        verbose_name_plural = '8. Ίδιο Χρώμα Προϊόντα'

    def __str__(self):
        return self.title.title


class SizeAttributeManager(models.Manager):
    def active_for_site(self):
        return super(SizeAttributeManager, self).filter(qty__gte=0)

    def instance_queryset(self, instance):
        return self.active_for_site().filter(product_related=instance)


class SizeAttribute(models.Model):
    title = models.ForeignKey(Size, on_delete=models.CASCADE, verbose_name='Νούμερο')
    product_related = models.ForeignKey(Product, null=True, on_delete=models.CASCADE, verbose_name='Προϊόν')
    qty = models.DecimalField(default=0, decimal_places=2, max_digits=6, verbose_name='Ποσότητα')
    order_discount = models.IntegerField(null=True, blank=True, default=0,verbose_name="'Εκπτωση Τιμολογίου σε %")
    price_buy = models.DecimalField(decimal_places=2,max_digits=6,default=0,verbose_name="Τιμή Αγοράς") # the price which you buy the product
    my_query = SizeAttributeManager()
    objects = models.Manager()

    class Meta:
        verbose_name_plural = '2. Μεγεθολόγιο'
        unique_together = ['title', 'product_related']

    def save(self, *args, **kwargs):
        get_sizes = SizeAttribute.objects.filter(product_related=self.product_related)
        
        super(SizeAttribute, self).save(*args, **kwargs)
        self.product_related.qty = get_sizes.aggregate(Sum('qty'))['qty__sum'] if get_sizes else 0
        self.product_related.save()

    def __str__(self):
        return '%s - %s'%(self.product_related, self.title)

    def check_product_in_order(self):
        return str(self.product_related + '. Χρώμα : ' + self.title.title + ', Μέγεθος : ' + self.title.title)

    def delete_update_product(self):
        self.product_related.qty -= self.qty
        self.product_related.save()

    def tag_final_price(self):
        final_price = self.product_related.final_price if not self.product_related.price_buy == self.price_buy else self.price_buy
        return '%s %s' % (final_price, CURRENCY)
    tag_final_price.short_description = 'Τιμή Αγοράς'


class ProductPhotos(models.Model):
    image = models.ImageField()
    alt = models.CharField(null=True, blank=True, max_length=200, help_text='Θα δημιουργηθεί αυτόματα εάν δεν συμπληρωθεί')
    title = models.CharField(null=True ,blank=True, max_length=100, help_text='Θα δημιουργηθεί αυτόματα εάν δεν συμπληρωθεί')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False, verbose_name='Αρχική Εικόνα')
    is_back = models.BooleanField(default=False, verbose_name='Δεύτερη Εικόνα')

    class Meta:
        verbose_name_plural = 'Gallery'

    def __str__(self):
        return self.title

    def image_status(self):
        return 'Primary Image' if self.is_primary else 'Secondary Image' if self.is_back else 'Image'

    def image_tag(self):
        return mark_safe('<img width="150px" height="150px" src="%s%s" />' %(MEDIAURL, self.image))
    image_tag.short_description = 'Εικονα'

    def image_tag_tiny(self):
        return mark_safe('<img width="150px" height="150px" src="%s%s" />' %(MEDIAURL, self.image))
    image_tag_tiny.short_description = 'Εικόνα'

    def tag_status(self):
        return 'First Picture' if self.is_primary else 'Back Picture' if self.is_back else 'Picture'
#  --------------------------------------------------------------------------------------------------


class ChangeQtyOrder(models.Model):
    title = models.CharField(max_length=64, unique=True, verbose_name='Σχολιασμός')
    day_added = models.DateField(auto_now=True)

    def __str__(self):
        return self.title


class ChangeQtyOrderItem(models.Model):
    title = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(ChangeQtyOrder, on_delete=models.CASCADE)
    qty = models.DecimalField(default=0, max_digits=6, decimal_places=2)
    size = models.ForeignKey(SizeAttribute, blank=True, null=True, on_delete=models.CASCADE)

    def show_product(self):
        return self.title


class ChangeQtyOrderItemSize(models.Model):
    title = models.ForeignKey(SizeAttribute, on_delete=models.CASCADE)
    order = models.ForeignKey(ChangeQtyOrder, on_delete=models.CASCADE)
    qty = models.DecimalField(default=0, max_digits=6, decimal_places=2)

    def show_product(self):
        return self.title
