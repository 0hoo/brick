# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-15 01:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sets', '0005_product_is_approved'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebayitem',
            name='available',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
