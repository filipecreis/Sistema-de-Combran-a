# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2023-05-19 19:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20230519_1343'),
    ]

    operations = [
        migrations.AddField(
            model_name='type_billing',
            name='parcela_venda',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='type_billing',
            name='venda',
            field=models.FloatField(default=0),
        ),
    ]