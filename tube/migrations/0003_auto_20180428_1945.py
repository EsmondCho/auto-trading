# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-28 10:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tube', '0002_auto_20180428_1937'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderinfo',
            name='order_type',
            field=models.IntegerField(choices=[(0, 'BID'), (1, 'ASK')]),
        ),
    ]
