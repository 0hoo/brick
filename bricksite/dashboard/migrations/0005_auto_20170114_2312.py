# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-14 23:12
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0004_auto_20170108_0358'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dashboard',
            name='new_average_ebay_price',
        ),
        migrations.RemoveField(
            model_name='dashboard',
            name='new_average_price',
        ),
        migrations.RemoveField(
            model_name='dashboard',
            name='new_max_ebay_price',
        ),
        migrations.RemoveField(
            model_name='dashboard',
            name='new_max_price',
        ),
        migrations.RemoveField(
            model_name='dashboard',
            name='new_min_ebay_price',
        ),
        migrations.RemoveField(
            model_name='dashboard',
            name='new_min_price',
        ),
        migrations.RemoveField(
            model_name='dashboard',
            name='used_average_ebay_price',
        ),
        migrations.RemoveField(
            model_name='dashboard',
            name='used_average_price',
        ),
        migrations.RemoveField(
            model_name='dashboard',
            name='used_max_ebay_price',
        ),
        migrations.RemoveField(
            model_name='dashboard',
            name='used_max_price',
        ),
        migrations.RemoveField(
            model_name='dashboard',
            name='used_min_ebay_price',
        ),
        migrations.RemoveField(
            model_name='dashboard',
            name='used_min_price',
        ),
    ]
