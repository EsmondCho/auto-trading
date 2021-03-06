# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-07 07:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=40)),
                ('symbol', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Exchange',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('counter', models.IntegerField(verbose_name='counter_currency_id')),
                ('base', models.IntegerField(verbose_name='base_currency_id')),
                ('euid', models.CharField(max_length=255)),
                ('amount', models.DecimalField(decimal_places=8, max_digits=32)),
                ('price', models.DecimalField(decimal_places=8, max_digits=32)),
                ('total', models.DecimalField(decimal_places=8, max_digits=32)),
                ('registered_time', models.DateTimeField(auto_now_add=True)),
                ('modified_time', models.DateTimeField(auto_now=True, null=True)),
                ('exchange', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exchange.Exchange')),
            ],
        ),
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exchange.Type'),
        ),
    ]
