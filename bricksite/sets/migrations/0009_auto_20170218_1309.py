# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-18 13:09
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sets', '0008_auto_20170218_0841'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bricklinkrecord',
            old_name='product',
            new_name='brickset',
        ),
    ]
