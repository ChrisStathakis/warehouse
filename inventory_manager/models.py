from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import Sum, F, Q
from django.dispatch import receiver
from django.db.models.signals import pre_delete

from products.models import *
from dashboard.models import PaymentOrders
from decimal import Decimal
import os

from model_utils import FieldTracker


def upload_image(instance, filename):
    return 'warehouse_orders/{0}/{1}'.format(instance.order_related.code, filename)


def validate_file(value):
    if value.size > 3.0*1024*1024:
        raise ValidationError('Το αρχείο είναι μεγαλύτερο από 3mb')
    get_extension = os.path.splitext(value.name)[1]
    valid_extensions = ['.pdf', '.jpg', '.xls', '.xlsx', '.jpg', '.png']
    if not get_extension.lower() in valid_extensions:
        raise ValidationError('We dont support that type of file!')


def vaidate_image(value):
    return value


def check_taxes(taxes_choice):
    if taxes_choice == '1':
        return 13
    if taxes_choice == '2':
        return 23
    if taxes_choice == '3':
        return 24
    if taxes_choice == '4':
        return 0


class OrderManager(models.Manager):
    def pending_orders(self):
        return super(OrderManager, self).filter(is_paid=False).order_by('day_created')

    def complete_orders(self):
        return super(OrderManager, self).filter(is_paid=True).order_by('day_created')


class Order(models.Model):
    code = models.CharField(max_length=40, verbose_name="Αριθμός Παραστατικού")
    vendor = models.ForeignKey(Supply, verbose_name="Προμηθευτής", on_delete=models.CASCADE)
    day_created = models.DateTimeField(auto_created=True, default=datetime.datetime.now(), verbose_name='Ημερομηνία') # primary mother fucker
    date_created = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(null=True, blank=True, verbose_name="")
    payment_method = models.CharField(max_length=1, choices=PAYMENT_TYPE, default='2')
    total_price_no_discount = models.DecimalField(default=0, max_digits=15, decimal_places=2, verbose_name="Αξία προ έκπτωσης")
    total_discount = models.DecimalField(default=0, max_digits=15, decimal_places=2, verbose_name="Αξία έκπτωσης")
    total_price_after_discount = models.DecimalField(default=0, max_digits=15, decimal_places=2, verbose_name="Αξία μετά την έκπτωση")
    total_taxes = models.DecimalField(default=0, max_digits=15, decimal_places=2, verbose_name="Φ.Π.Α")
    total_price = models.DecimalField(default=0, max_digits=15, decimal_places=2, verbose_name="Τελική Αξία")
    paid_value = models.DecimalField(default=0, max_digits=15, decimal_places=2, verbose_name="Πληρωμένο Ποσό")
    taxes_modifier = models.CharField(max_length=1, choices=TAXES_CHOICES, default='3')

    objects = models.Manager()
    my_query = OrderManager()
    tracker = FieldTracker()
    payment_orders = GenericRelation(PaymentOrders)

    is_paid = models.BooleanField(default=False, verbose_name='Πληρώθηκε')

    class Meta:
        verbose_name_plural = "1. Τιμολόγια"

    def __str__(self):
        return self.code
    
    def save(self, *args, **kwargs):
        all_order_items = self.orderitem_set.all()
        self.total_price_no_discount = all_order_items.aggregate(total=Sum(F('qty')*F('price')))['total'] if \
            all_order_items else 0
        self.total_discount = self.total_price_no_discount
        self.total_price_after_discount = self.total_price_no_discount - self.total_discount
        self.total_taxes = self.total_price_after_discount * (100-Decimal(self.get_taxes_modifier_display()))/100
        self.total_price = self.total_price_after_discount - self.total_taxes

        if self.is_paid:
            get_orders = self.payment_orders.all()
            get_orders.update(is_paid=True)
        self.paid_value = self.payment_orders.filter(is_paid=True).aggregate(Sum('value'))['value__sum'] if self.payment_orders.filter(is_paid=True) else 0
        self.paid_value = self.paid_value if self.paid_value else 0

        if self.paid_value >= self.total_price and self.paid_value > 0.5:
            self.is_paid = True

        if self.is_paid and self.paid_value < self.total_price:
            get_diff = self.total_price - self.paid_value
            new_payment = PaymentOrders.objects.create(date_expired=self.day_created,
                                                       value=get_diff,
                                                       payment_type=self.payment_method,
                                                       is_paid=True,
                                                       title='%s' % self.code if self.code else 'Τιμολόγιο %s' % self.id,
                                                       content_type=ContentType.objects.get_for_model(Order),
                                                       object_id=self.id
                                                       )

        if not self.date_created:
            self.date_created = self.day_created
        super(Order, self).save(*args, **kwargs)
        self.vendor.save()
            
    def images_query(self):
        return self.warehouseorderimage_set.all()

    def absolute_url_order(self):
        return reverse('order_edit_main', kwargs={'dk': self.id})

    @property
    def get_remaining_value(self):
        return round(self.total_price - self.paid_value, 2)

    def tag_remaining_value(self):
        return '%s %s' % (self.get_remaining_value, CURRENCY)

    def tag_all_values(self):
        clean_value = '%s %s' % (self.total_price_no_discount, CURRENCY)
        discount = '%s %s' % (self.total_discount, CURRENCY)
        value_after_discount = '%s %s' % (self.total_price_after_discount, CURRENCY)
        taxes = '%s %s' % (self.total_taxes, CURRENCY)
        total_value = '%s %s' % (self.total_price, CURRENCY)
        return [clean_value, discount, value_after_discount, taxes, total_value]

    def tag_clean_value(self):
        return self.tag_all_values()[0]
    tag_clean_value.short_description = 'Καθαρή Αξία'

    def tag_value_after_discount(self):
        return self.tag_all_values()[2]
    tag_value_after_discount.short_description = 'Αξία Μετά την έκπτωση'

    def tag_total_value(self):
        return self.tag_all_values()[4]
    tag_total_value.short_description = 'Τελική Αξία'

    def tag_paid_value(self):
        return '%s %s' %(self.paid_value, CURRENCY)
    tag_paid_value.short_description = 'Πληρωμένη Αξία'


class WarehouseOrderImage(models.Model):
    order_related = models.ForeignKey(Order, on_delete=models.CASCADE)
    file = models.FileField(upload_to=upload_image, null=True, validators=[validate_file, ])
    is_first = models.BooleanField(default=True)

    def __str__(self):
        return '%s-%s' % (self.order_related.code, self.id)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name='Προϊόν',
                                on_delete=models.CASCADE,
                                null=True,
                                )
    unit = models.CharField(max_length=1, choices=UNIT, default='1')
    discount = models.IntegerField(default=0, verbose_name='Εκπτωση %')
    taxes = models.CharField(max_length=1, choices=TAXES_CHOICES, default='3')
    qty = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Ποσότητα')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Τιμή Μονάδας', blank=True, )
    size = models.ForeignKey(SizeAttribute, verbose_name='Size', null=True, blank=True, on_delete=models.CASCADE)
    total_clean_value = models.DecimalField(default=0, max_digits=15, decimal_places=2, verbose_name='Συνολική Αξία χωρίς Φόρους')
    total_value_with_taxes = models.DecimalField(default=0, max_digits=14, decimal_places=2, verbose_name='Συνολική Αξία με φόρους')
    day_added = models.DateField(blank=True, null=True)

    tracker = FieldTracker()

    class Meta:
        ordering = ['product']
        verbose_name = "Συστατικά Τιμολογίου   "

    def save(self, *args, **kwargs):
        vendor, order, product = self.order.vendor, self.order, self.product
        # old_qty = self.tracker.previous('qty')
        # is_change = self.tracker.has_changed('qty')
        self.taxes = self.order.taxes_modifier
        self.total_clean_value = self.qty * self.get_clean_price
        self.total_value_with_taxes = self.total_clean_value * ((100+Decimal(self.get_taxes_display()))/100)
        super(OrderItem, self).save(*args, **kwargs)
        product.price_buy = self.price
        product.order_discount = self.discount
        product.measure_unit = self.unit
        product.save()

    def __str__(self):
        return 'Order Item %s' % self.id

    @property
    def get_clean_price(self):
        return self.price * ((100-Decimal(self.discount))/100)

    @property
    def get_final_price(self):
        return round(self.get_clean_price * self.qty, 2)

    def tag_price(self):
        return '%s %s' % (self.price, CURRENCY)

    def tag_qty(self):
        return '%s %s' % (self.qty, self.unit)

    def tag_clean_price(self):
        return '%s %s' % (round(self.get_clean_price, 2), CURRENCY)

    def tag_final_price(self):
        return '%s %s' % (self.get_final_price, CURRENCY)

    @property
    def get_total_clean_price(self):
        return (self.price*self.qty)*((100-Decimal(self.discount))/100) if self.price and self.qty else 0

    @property
    def get_total_final_price(self):
        return self.get_total_clean_price*((100+Decimal(self.get_taxes_display()))/100) if self.price and self.qty else 0

    def tag_total_clean_price(self):
        return '%s %s' % (round(self.get_total_clean_price, 2), CURRENCY)
    tag_total_clean_price.short_description = 'Καθαρή Αξία'

    def tag_total_final_price(self):
        return '%s %s' % (round(self.get_total_final_price, 2), CURRENCY)
    tag_total_final_price.short_description = 'Τελική Αξία'


@receiver(pre_delete, sender=OrderItem)
def update_qty_on_delete(sender, instance, *args, **kwargs):
    product = instance.product
    order = instance.order
    self = instance
    product.qty -= instance.qty
    product.save()
    get_all_items = OrderItem.objects.filter(order=order)
    first_price = get_all_items.aggregate(total=Sum(F('qty') * F('price')))['total'] if get_all_items else 0
    price_after_discount = first_price * ((100 - Decimal(self.discount)) / 100)
    price_after_taxes = price_after_discount * ((100 + Decimal(self.get_taxes_display())) / 100)
    self.order.total_price_no_discount, self.order.total_price_after_discount, self.order.total_price = first_price, price_after_discount, price_after_taxes
    self.order.total_discount, self.order.total_taxes = price_after_discount - first_price, price_after_taxes - price_after_discount
    self.order.save()


class PreOrder(models.Model):
    STATUS= (('a','Active'), ('b','Used'))
    title = models.CharField(max_length=100)
    status = models.CharField(max_length=1, choices=STATUS, default='a')
    day_added = models.DateField(auto_now=True)

    def __str__(self):
        return self.title


class PreOrderItem(models.Model):
    title = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(PreOrder, on_delete=models.CASCADE)
    qty = models.DecimalField(decimal_places=2, max_digits=5)
    day_added = models.DateField(auto_now=True)

    def __str__(self):
        return self.title.title


class PreOrderNewItem(models.Model):
    title = models.CharField(max_length=120)
    vendor = models.ForeignKey(Supply, on_delete=models.CASCADE)
    qty = models.DecimalField(max_digits=6,decimal_places=2)
    price_buy = models.DecimalField(default=0,max_digits=6,decimal_places=2, verbose_name='Τιμή Αγοράς')
    discount_buy = models.IntegerField(default=0, verbose_name='Εκπτωση Τιμολογίου')
    price = models.DecimalField(default=0,max_digits=6,decimal_places=2, verbose_name='Τιμή Λιανικής')
    sku = models.CharField(max_length=50, blank=True, null=True)
    category = models.ForeignKey(Category, null=True, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brands, blank=True,null=True, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, blank=True, null=True, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, blank=True, null=True, on_delete=models.CASCADE)

    day_added = models.DateField(auto_now=True)
    order = models.ForeignKey(PreOrder, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class PreOrderStatement(models.Model):
    STATUS=(('a','Ενεργό'),{'b','Στάλθηκε.'})
    STATUS_P=(('a','Ενεργό'),{'b','Εκτυπώθηκε.'})
    title = models.CharField(max_length=100)
    day_added = models.DateField(auto_now=True)
    day_expire = models.DateField(auto_now=True)
    vendor = models.ForeignKey(Supply, on_delete=models.CASCADE)
    send_status = models.BooleanField(default=False)
    is_sended  = models.CharField(max_length=1, choices=STATUS, default='a')
    print_status = models.BooleanField(default=False)
    is_printed = models.CharField(default='a', max_length=1, choices=STATUS_P)
    consume_to_order = models.BooleanField(default=False, verbose_name='Μετατροπή σε Τιμολόγιο.')

    def __str__(self):
        return self.title


class PreOrderStatementItem(models.Model):
    title = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(PreOrderStatement, on_delete=models.CASCADE)
    qty = models.DecimalField(decimal_places=2, max_digits=5)
    day_added = models.DateField(auto_now=True)

    def __str__(self):
        return self.title.title


class PreOrderStatementNewItem(models.Model):
    title = models.CharField(max_length=120)
    vendor = models.ForeignKey(Supply, on_delete=models.CASCADE)
    qty = models.DecimalField(max_digits=6,decimal_places=2)
    price_buy = models.DecimalField(default=0,max_digits=6,decimal_places=2,verbose_name='Τιμή Αγοράς')
    discount_buy = models.IntegerField(default=0, verbose_name='Εκπτωση Τιμολογίου')
    price = models.DecimalField(default=0,max_digits=6,decimal_places=2, verbose_name='Τιμή Λιανικής')
    sku = models.CharField(max_length=50, blank=True, null=True)
    category = models.ForeignKey(Category, null=True, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brands, blank=True,null=True, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, blank=True, null=True, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, blank=True, null=True, on_delete=models.CASCADE)

    day_added = models.DateField(auto_now=True)
    order = models.ForeignKey(PreOrderStatement, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
