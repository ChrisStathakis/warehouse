from django.db import models
from products.models import *
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, PAYMENT_TYPE

CHOICES_ = (('a', 'Σε εξέλιξη'), ('b', 'Εισπράκτηκε'), ('c', 'Ακυρώθηκε'),)


class PayOrdersManager(models.Manager):

    def checks(self):
        return super(PayOrdersManager, self).filter(payment_type='c')

    def orders_payments(self):
        return super(PayOrdersManager, self).filter(payment_type='a')

    def deposit_orders(self):
        return super(PayOrdersManager, self).filter(payment_type='b')


class PayOrders(models.Model):
    title = models.ForeignKey(Order, verbose_name='Αριθμός Παραστατικου', blank=True, null=True, on_delete=models.CASCADE)
    day_created = models.DateField(verbose_name='Ημερομηνία', auto_now_add=True)
    date_expired = models.DateField(verbose_name='Ημερομηνία Εξόφλησης')
    payment_method = models.CharField(default='3', max_length=1, choices=PAYMENT_TYPE)
    receipt = models.CharField(max_length=64, default='---', verbose_name='Απόδειξη')
    value = models.DecimalField(default=0, max_digits=20, decimal_places=2, verbose_name='Ποσό')
    status = models.CharField(max_length=1, choices=CHOICES_, default='a', verbose_name='Κατάσταση')
    vendor = models.ForeignKey(Vendor, null=True, on_delete=models.CASCADE)
    objects = models.Manager()
    my_query = PayOrdersManager()

    class Meta:
        verbose_name = "Εντολές Πληρωμής"

    def __str__(self):
        return '%s' % (self.receipt)

    def delete_pay(self):
        self.title.credit_balance -= self.value
        self.title.status = 'd'
        self.title.save()
        self.title.vendor.balance += self.value
        self.title.vendor.save()

    def delete_pay_order(self):
        self.vendor.remaining_deposit += self.value
        self.vendor.balance += self.value
        self.vendor.save()
        self.title.credit_balance -= self.value
        self.title.save()

    def delete_pay_order_from_order(self):
        self.vendor.balance += self.value
        self.vendor.save()
        self.title.credit_balance -= self.value
        self.title.save()

        self.title.status = 'a'
        self.title.save()

    def payment_type_vendor_page(self):
        return 'payment_order'

    def intentity(self):
        return 'Πληρωμή Τιμ. %s ---  Προμ. %s' % (self.title.code, self.title.vendor)

    def tag_value(self):
        return '%s %s' % (self.value, CURRENCY)





