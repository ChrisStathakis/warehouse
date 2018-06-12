# Generated by Django 2.0 on 2018-06-07 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transcations', '0003_auto_20180607_1440'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='vacation',
            options={'ordering': ['status', 'date_started', 'date_end']},
        ),
        migrations.AddField(
            model_name='vacation',
            name='status',
            field=models.BooleanField(default=False, verbose_name='Ολοκληρώθηκε'),
        ),
    ]