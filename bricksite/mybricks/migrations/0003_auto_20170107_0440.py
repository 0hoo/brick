# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-07 04:40
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mybricks', '0002_thing'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='buying_price',
        ),
        migrations.RemoveField(
            model_name='item',
            name='owned',
        ),
        migrations.RemoveField(
            model_name='item',
            name='quantity',
        ),
        migrations.RemoveField(
            model_name='item',
            name='wish',
        ),
    ]
