# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2023-06-14 01:03
from __future__ import unicode_literals

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20230613_1412'),
    ]

    operations = [
        migrations.AlterField(
            model_name='type_billing',
            name='data_atualizacao',
            field=models.DateField(default=core.models.proxima_atualizacao),
        ),
    ]