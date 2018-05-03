# Generated by Django 2.0.2 on 2018-05-03 04:55

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_manager', '0060_auto_20180503_0740'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='day_created',
            field=models.DateTimeField(auto_created=True, default=datetime.datetime(2018, 5, 3, 7, 55, 11, 872653), verbose_name='Ημερομηνία'),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='dashboard.PaymentMethod'),
        ),
    ]
