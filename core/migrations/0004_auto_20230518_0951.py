# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2023-05-18 12:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20230518_0947'),
    ]

    operations = [
        migrations.AlterField(
            model_name='produto',
            name='status',
            field=models.BooleanField(choices=[(True, 'Ativo'), (False, 'Desativado')]),
        ),
    ]
