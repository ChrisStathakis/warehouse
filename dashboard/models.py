from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from django.db.models.signals import post_delete, pre_save
from django.utils import timezone
from django.db.models import Sum

from .constants import *


MEASURE_UNITS = (
    ('1', 'Τεμάχια'),
    ('2', 'Κιλά'),
    ('3', 'Κιβώτια')
    )

STATUS = (('1', ''),('2', ''),('3', ''),('4', ''),)


class PaymentOrders(models.Model):
    is_paid = models.BooleanField(default=False)
    title = models.CharField(max_length=150, blank=True, null=True)
    date_expired = models.DateField(auto_created=True)
    date_created = models.DateTimeField(blank=True, null=True)
    payment_type = models.CharField(max_length=1, choices=PAYMENT_TYPE, default='1')
    value = models.DecimalField(max_digits=50, decimal_places=2, default=0)
    bank = models.CharField(max_length=1, choices=BANKS, default='0')
    is_expense = models.BooleanField(default=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['-date_expired', ]

    def __str__(self):
        return "Επιταγη %s" % self.id

    def save(self, *args, **kwargs):
        if not self.date_created:
            self.date_created = self.date_expired
        super(PaymentOrders, self).save(*args, **kwargs)
        get_order = self.content_object
        get_order.save()

    def tag_value(self):
        return '%s %s' % (self.value, CURRENCY)

    def tag_is_paid(self):
        return 'PAID' if self.is_paid else 'NOT PAID'

    def status(self):
        return 'Πληρωμένο' if self.is_paid else 'Μη Πληρωμένο'

    def tag_payment(self):
        return '%s - %s' % (self.get_payment_type_display(), self.bank) if self.bank != "0" else self.get_payment_type_display()


@receiver(post_delete, sender=PaymentOrders)
def update_on_delete(sender, instance, *args, **kwargs):
    get_order = instance.content_object
    get_order.is_paid = False
    get_order.save()


class Store(models.Model):
    title = models.CharField(max_length=150, unique=True)
    margin = models.IntegerField(default=0)
    markup = models.IntegerField(default=0)

    def __str__(self):
        return self.title
