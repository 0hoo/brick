# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-20 00:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mybricks', '0010_auto_20170218_1408'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mybrick',
            options={'verbose_name': 'My Brick'},
        ),
        migrations.AlterModelOptions(
            name='mybrickitem',
            options={'verbose_name': 'My Brick Item'},
        ),
        migrations.AlterModelOptions(
            name='mybrickrecord',
            options={'get_latest_by': 'created', 'ordering': ('-created',), 'verbose_name': 'My Brick Record'},
        ),
        migrations.AlterField(
            model_name='mybrickitem',
            name='mybrick',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item_set', to='mybricks.MyBrick'),
        ),
    ]
