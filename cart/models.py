from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Sum, F
from django.dispatch import receiver
from django.db.models.signals import post_delete
from dashboard.constants import PAYMENT_TYPE
from products.models import Product, SizeAttribute, CategorySite

from decimal import Decimal
import datetime
# Create your models here.

CURRENCY = settings.CURRENCY


def validate_positive_decimal(value):
    if value < 0:
        return ValidationError('This number is negative!')
    return value


class Country(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(unique=True, max_length=100)

    def __str__(self):
        return self.title


class CouponManager(models.Manager):

    def active_coupons(self):
        return super(CouponManager, self).filter(active=True)

    def active_date(self, date,):
        return self.active_coupons().filter(date_created__lte=date, date_end__gte=date)


class Coupons(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(unique=True, max_length=50)
    code = models.CharField(unique=True, null=True, max_length=50)
    date_created = models.DateTimeField()
    date_end = models.DateTimeField()
    cart_total_value = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    products = models.ManyToManyField(Product, blank=True)
    categories = models.ManyToManyField(CategorySite, blank=True)
    discount_value = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=10)
    discount_percent = models.PositiveIntegerField(blank=True, null=True)

    objects = models.Manager()
    my_query = CouponManager()

    class Meta:
        ordering = ['active', ]
        verbose_name_plural = 'Coupons'

    def __str__(self):
        return self.title

    def check_coupon(self, order_type, order, order_items, coupons):
        # order_type 'cart' or 'eshop'
        if self in Coupons.my_query.active_date(date=datetime.datetime.now()):
            if order_type == 'cart':
                if order.value > self.cart_total_value:
                    order.coupon_discount += self.discount_value if self.discount_value else \
                    (self.discount_percent/100)*order.value if self.discount_percent else 0
                if self.categories or self.products:
                    pass
            if order_type == 'eshop':
                order.discount += self.discount_value if self.discount_value else \
                    (self.discount_percent/100)*order.value if self.discount_percent else 0


class Shipping(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(unique=True, max_length=100)
    cost = models.DecimalField(max_digits=6, default=0, decimal_places=2, validators=[validate_positive_decimal, ])
    active_cost = models.BooleanField(default=True)
    active_minimum_cost = models.DecimalField(default=40, max_digits=6, decimal_places=2,
                                              validators=[validate_positive_decimal, ])
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def estimate_cost(self, price):
        return self.cost if price < self.active_minimum_cost and self.active_cost else 0


class CartManager(models.Manager):

    def active_carts(self):
        return super(CartManager, self).filter(active=True)

    def current_cart(self, session_id):
        get_cart = super(CartManager, self).filter(id_session=session_id, active=True)
        return get_cart.last() if get_cart else None


class Cart(models.Model):
    active = models.BooleanField(default=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    id_session = models.CharField(max_length=50)
    date_created = models.DateTimeField(auto_now=True)
    value = models.DecimalField(default=0, max_digits=10, decimal_places=2, validators=[validate_positive_decimal, ])
    is_complete = models.BooleanField(default=False)
    my_query = CartManager()
    objects = models.Manager()
    shipping_method = models.ForeignKey(Shipping, blank=True, null=True, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=1, choices=PAYMENT_TYPE, default='a')
    coupon = models.ManyToManyField(Coupons, blank=True)
    coupon_discount = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    final_value = models.DecimalField(decimal_places=2, max_digits=10, default=0)

    class Meta:
        ordering = ['-id']

    def check_coupons(self):
        try:
            all_coupons = self.coupon.all()
            price = self.value
            order_items = self.cartitem_set.all()
            for coupon in all_coupons:
                # priority
                limit_price = coupon.cart_total_value if coupon.cart_total_value else 0
                if price>limit_price and limit_price>0:
                    self.coupon_discount = coupon.discount_value if coupon.discount_value else \
                        (coupon.discount_percent/100)*price if coupon.discount_percent else 0
                if coupon.products or coupon.categories:
                    for product in order_items:
                        get_products = Product.objects.filter(category_site__in=coupon.categories.all()) if coupon.categories else []
                        if product in coupon.products.all() or product in get_products:
                            self.coupon_discount = coupon.discount_value if coupon.discount_value else \
                                (coupon.discount_percent / 100) * price if coupon.discount_percent else 0
        except:
            pass

    def __str__(self):
        return '%s %s' % ('Cart ', self.id)

    def save(self, *args, **kwargs):
        get_items = self.cartitem_set.all()
        self.value = get_items.aggregate(total=(Sum(F('final_price') * F('qty'), output_field=models.DecimalField())))['total'] if get_items else 0
        self.check_coupons()
        self.final_price = self.value - self.coupon_discount
        super(Cart, self).save(*args, **kwargs)

    def tag_value(self):
        return '%s %s' % (self.value, CURRENCY)

    def tag_final_value(self):
        return '%s %s' % (self.final_value, CURRENCY)

    def tag_payment_cost(self):
        return '%s %s' % (round(self.payment_method.cost, 2), CURRENCY) if self.payment_method else 0

    def tag_shipping_cost(self):
        return '%s %s' % (round(self.shipping_method.estimate_cost(self.value),2), CURRENCY) if self.shipping_method else 0

    @property
    def get_total_value(self):
        get_value = self.value
        if self.shipping_method:
            get_value = self.value + self.shipping_method.cost if\
                self.shipping_method.active_cost and self.value < self.shipping_method.active_minimum_cost \
                else self.value
        if self.payment_method:
            get_value = get_value + self.payment_method.cost
        return get_value

    def tag_total_value(self):
        return '%s %s' % (self.get_total_value, CURRENCY)

    def remove_cart_item(self, cart_item):
        self.value -= cart_item.get_total_price
        self.save()

    def to_order(self, payment_method, shipping_method):
        self.active, self.is_complete = False, True
        self.payment_method, self.shipping_method = PAYMENT_TYPE['%s'] % payment_method,\
                                                    Shipping.objects.get(id=int(shipping_method))
        self.save()


class CartItemManager(models.Manager):

    def check_if_exists(self, order_related, product):
        return super(CartItemManager, self).filter(order_related=order_related,
                                                   product_related=product
                                                   )


class CartItem(models.Model):
    order_related = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product_related = models.ForeignKey(Product, null=True, on_delete=models.CASCADE)
    id_session = models.CharField(max_length=50)
    qty = models.PositiveIntegerField(default=1)
    characteristic = models.ForeignKey(SizeAttribute, blank=True, null=True, on_delete=models.CASCADE)
    price = models.DecimalField(default=0, decimal_places=2, max_digits=10,
                                validators=[validate_positive_decimal,
                                            ])
    price_discount = models.DecimalField(default=0, decimal_places=2, max_digits=10,
                                         validators=[validate_positive_decimal, ]
                                         )
    final_price = models.DecimalField(default=0, decimal_places=2, max_digits=10, validators=[validate_positive_decimal,])
    my_query = CartItemManager()
    objects = models.Manager()

    def __str__(self):
        return self.product_related.title

    def save(self, *args, **kwargs):
        self.final_price = self.price_discount if self.price_discount > 0 else self.price
        super(CartItem, self).save(*args, **kwargs)
        self.order_related.save()

    @property
    def get_price(self):
        return Decimal(self.price) * ((100-Decimal(self.price_discount))/100)

    @property
    def get_total_price(self):
        return self.get_price*Decimal(self.qty)

    def tag_price(self):
        return '%s %s' % (round(self.get_price, 2), CURRENCY)

    def tag_total_price(self):
        return '%s %s' % (round(self.get_total_price, 2), CURRENCY)

    def tag_final_price(self):
        return '%s %s' % (self.final_price, CURRENCY)

    def tag_total_value(self):
        total_value = self.qty*self.final_price
        return '%s %s' % (total_value, CURRENCY)

    def update_order(self):
        items_query = CartItem.objects.filter(order_related=self.order_related)
        print(items_query)
        print(items_query.aggregate(total=Sum(F('qty')*F('final_price')))['total'] if items_query.exists() else 0)
        self.order_related.value += items_query.aggregate(total=Sum(F('qty')*F('final_price')))['total'] if items_query.exists() else 0
        self.order_related.save()

    def edit_cart_item(self, old_price):
        self.order_related.value -= old_price
        self.order_related.value += Decimal(self.get_total_price)
        self.order_related.save()

    def delete_from_order(self):
        self.order_related.value -= self.price
        self.order_related.save()
        if not self.qty == 1:
            self.qty -= 1
            self.save()
        else:
            self.delete()

    @staticmethod
    def create_cart_item(order, product, qty, size=None):
        qs_exists = CartItem.objects.filter(order_related=order, product_related=product)
        if qs_exists:
            cart_item = qs_exists.last()
            cart_item.qty += qty
            cart_item.save()
        else:
            new_cart_item = CartItem.objects.create(order_related=order,
                                                    product_related=product,
                                                    qty=qty,
                                                    price=product.price,
                                                    price_discount=product.price_discount,
                                                    id_session=order.id_session,
                                                    )
            if size:
                new_cart_item.characteristic = size
                new_cart_item.save()

@receiver(post_delete, sender=CartItem)
def update_order_on_delete(sender, instance, *args, **kwargs):
    get_order = instance.order_related
    get_order.save()


class CartRules(models.Model):
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    coupons = models.ManyToManyField(Coupons)
    country = models.ForeignKey(Country, blank=True, null=True, on_delete=models.CASCADE)
    payment_value = models.PositiveIntegerField(default=0)
    shipping_value = models.PositiveIntegerField(default=0)

    def estimate_shipping_value(self):
        value = self.cart.value
        shipping_method = self.cart.shipping_method
        shipping_value = 5
        if shipping_method:
            shipping_value = shipping_method.value if shipping_method.value_limit < value else 0
        return shipping_value

    def estimate_payment_type(self):
        payment_method = self.cart.payment_method
        payment_value = 2
        if payment_method:
            payment_value = 5 if payment_method == 1 and payment_method else 0
        return payment_value

    def save(self, *args, **kwargs):
        self.payment_value = self.estimate_payment_type()
        self.shipping_value = self.estimate_shipping_value()
        super(CartRules, self).save(*args, **kwargs)

