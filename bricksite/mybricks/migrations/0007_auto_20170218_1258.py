# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-18 12:58
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mybricks', '0006_auto_20170218_1246'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ItemRecord',
            new_name='MyBrickRecord',
        ),
    ]
