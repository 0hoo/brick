# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-20 08:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_auto_20170209_1155'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dashboard',
            old_name='item_count',
            new_name='mybrick_count',
        ),
    ]
