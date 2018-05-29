from products.models import Product, SizeAttribute
from django.db import models
from .constants import *
from .models import PaymentMethod, Store
from django.contrib.auth.models import User


class DefaultOrderModel(models.Model):
    title = models.CharField(max_length=150)
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    date_expired = models.DateField(auto_created=True)
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Αξία Παραγγελίας')
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Έκπτωση', )
    taxes = models.CharField(max_length=1, choices=TAXES_CHOICES, default='3')
    paid_value = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Αποπληρωμένο Πόσο')
    final_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)
    payment_method = models.ForeignKey(PaymentMethod, null=True, on_delete=models.SET_NULL, )
    count_items = models.PositiveIntegerField(default=0)
    notes = models.TextField(null=True, blank=True)
    user_account = models.ForeignKey(User, blank=True, null=True, verbose_name='Χρήστης', on_delete=models.CASCADE)
    store_related = models.ForeignKey(Store, blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        abstract = True


    
class DefaultOrderItemModel(models.Model):
    title = models.ForeignKey(Product, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    value = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name='Τιμή Μονάδας')
    qty = models.DecimalField(max_digits=6, decimal_places=2, default=1, verbose_name='Ποσότητα')
    discount = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name='Τιμή Μονάδας Με έκπτωση.')
    final_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    size = models.ForeignKey(SizeAttribute, blank=True ,null=True, on_delete=models.CASCADE)
    
    class Meta:
        abstract = True