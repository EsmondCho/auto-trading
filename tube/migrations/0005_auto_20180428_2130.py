# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-28 12:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tube', '0004_eventlog_eventinfo_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventlog',
            name='eventinfo_id',
            field=models.IntegerField(null=True),
        ),
    ]
