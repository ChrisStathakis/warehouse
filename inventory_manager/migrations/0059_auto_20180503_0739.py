# Generated by Django 2.0.2 on 2018-05-03 04:39

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_manager', '0058_auto_20180430_0851'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='day_created',
            field=models.DateTimeField(auto_created=True, default=datetime.datetime(2018, 5, 3, 7, 39, 37, 285660), verbose_name='Ημερομηνία'),
        ),
    ]
