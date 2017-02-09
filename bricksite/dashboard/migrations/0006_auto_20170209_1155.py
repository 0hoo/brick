# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-09 11:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0005_auto_20170114_2312'),
    ]

    operations = [
        migrations.AddField(
            model_name='dashboard',
            name='sold_quantity',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dashboard',
            name='total_sold_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
            preserve_default=False,
        ),
    ]
