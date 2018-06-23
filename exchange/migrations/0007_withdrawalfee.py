# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-15 08:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', '0006_auto_20180415_1511'),
    ]

    operations = [
        migrations.CreateModel(
            name='WithdrawalFee',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('fee', models.DecimalField(decimal_places=8, max_digits=32)),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exchange.Currency')),
                ('exchange', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exchange.Exchange')),
            ],
        ),
    ]
