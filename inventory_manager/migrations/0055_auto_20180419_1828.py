# Generated by Django 2.0 on 2018-04-19 15:28

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_manager', '0054_auto_20180326_0951'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='day_created',
            field=models.DateTimeField(auto_created=True, default=datetime.datetime(2018, 4, 19, 18, 28, 56, 103331), verbose_name='Ημερομηνία'),
        ),
    ]
