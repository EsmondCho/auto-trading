# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-08 09:22
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', '0003_currencymap'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='currencymap',
            name='currency',
        ),
        migrations.RemoveField(
            model_name='currencymap',
            name='exchange',
        ),
        migrations.DeleteModel(
            name='CurrencyMap',
        ),
    ]