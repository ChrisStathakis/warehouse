from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from django.db.models import Sum, F

from decimal import Decimal
import slugify

from products.models import Product, CategorySite, Brands, ProductPhotos
from point_of_sale.models import OrderItem
from dashboard.models import *


@receiver(post_save, sender=Product)
def create_unique_slug_for_product(sender, instance, *args, **kwargs):
    if not instance.slug:
        slug = slugify.slugify(instance.title)
        qs_exists = Product.objects.filter(slug=slug)
        if qs_exists.exists():
            slug = '%s-%s' %(slug, instance.id)
        instance.slug = slug
        instance.save()
post_save.connect(create_unique_slug_for_product, sender=Product)


@receiver(post_delete, sender=Product)
def delete_related_instances(sender, instance, *args, **kwargs):
    images = ProductPhotos.objects.filter(product=instance)
    if images:
        for image in images:
            image.delete()


def create_slug_cat_site(instance, new_slug=None):
    slug = slugify.slugify(instance.title)
    if new_slug is not None:
        slug=new_slug
    qs = CategorySite.objects.filter(slug=slug).order_by('-id')
    exists = qs.exists()
    if exists:
        new_slug = '%s-%s'%(slug,qs.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug


#brand
def create_slug_brand(instance, new_slug=None):
    slug = slugify.slugify(instance.title)
    if new_slug is not None:
        slug=new_slug
    qs = Brands.objects.filter(slug=slug).order_by('-id')
    exists = qs.exists()
    if exists:
        new_slug = '%s-%s'%(slug,qs.first().id)
        return create_slug(instance,new_slug=new_slug)
    return slug


def create_slug(instance, new_slug=None):
    slug = slugify.slugify(instance.title)
    if new_slug is not None:
        slug=new_slug
    qs = Product.objects.filter(slug=slug).order_by('-id')
    exists = qs.exists()
    if exists:
        new_slug = '%s-%s'%(slug,qs.first().id)
        return create_slug(instance,new_slug=new_slug)
    return slug


@receiver(post_save, sender=CategorySite)
def create_unique_slug_cs(sender, instance,*args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug_cat_site(instance)
        instance.save()
post_save.connect(create_unique_slug_cs, sender=CategorySite)


@receiver(post_save, sender=Brands)
def create_unique_slug_for_brands(sender, instance,*args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug_brand(instance)
        instance.save()
post_save.connect(create_unique_slug_for_brands, sender=Brands)


@receiver(post_save, sender=ProductPhotos)
def create_title_and_alt(sender, instance, *args, **kwargs):
    if not instance.title:
        instance.title = '%s' %(instance.product.title)
        instance.save()
    if not instance.alt:
        instance.alt = '%s' %(instance.product.title)
        instance.save()
post_save.connect(create_title_and_alt, sender=ProductPhotos)


@receiver(post_delete, sender=OrderItem)
def update_qty_on_delete(sender, instance, *args, **kwargs):
    vendor, order, product = instance.order.vendor, instance.order, instance.product
    get_all_items = OrderItem.objects.filter(order=order)
    first_price = get_all_items.aggregate(total=Sum(F('qty')*F('price')))['total'] if get_all_items else 0
    price_after_discount = first_price*((100-Decimal(instance.discount))/100)
    price_after_taxes = price_after_discount * ((100+Decimal(instance.get_taxes_display()))/100)
    instance.order.total_price_no_discount, instance.order.total_price_after_discount, instance.order.total_price = first_price, price_after_discount, price_after_taxes
    instance.order.total_discount, instance.order.total_taxes = price_after_discount - first_price, price_after_taxes - price_after_discount
    instance.order.save()
    if not product.size:
        product.qty -= instance.qty
    product.save()

