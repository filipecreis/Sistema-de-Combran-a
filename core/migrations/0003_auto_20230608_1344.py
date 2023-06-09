# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2023-06-08 16:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20230530_1522'),
    ]

    operations = [
        migrations.RenameField(
            model_name='posto',
            old_name='email',
            new_name='email_responsavel',
        ),
        migrations.RenameField(
            model_name='posto',
            old_name='telefone',
            new_name='telefone_responsavel',
        ),
        migrations.RenameField(
            model_name='tipo_produto',
            old_name='codigo_equipamento',
            new_name='codigo_egestor',
        ),
        migrations.RemoveField(
            model_name='tipo_produto',
            name='descricao',
        ),
        migrations.RemoveField(
            model_name='type_billing',
            name='chave',
        ),
        migrations.RemoveField(
            model_name='type_billing',
            name='descricao',
        ),
        migrations.AddField(
            model_name='posto',
            name='id_egestor',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='type_billing',
            name='contrato',
            field=models.TextField(default='0'),
        ),
        migrations.AddField(
            model_name='type_billing',
            name='email_cobranca',
            field=models.CharField(default='0', max_length=100),
        ),
        migrations.AddField(
            model_name='type_billing',
            name='telefone_cobranca',
            field=models.CharField(default='0', max_length=100),
        ),
    ]
