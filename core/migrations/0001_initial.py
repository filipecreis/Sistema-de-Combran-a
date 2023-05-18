# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2023-05-17 16:27
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Billing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(0, 'Cancelado'), (1, 'Cobrança realizada'), (2, 'Pagamento efetuado')])),
                ('invoice_date', models.DateField(default=datetime.date.today)),
                ('pay_date', models.DateField(default=datetime.date.today)),
                ('encerrante', models.IntegerField(default=0)),
                ('quant_bonificado', models.FloatField(default=0)),
                ('quant_gerencial', models.FloatField(default=0)),
                ('quant_pago', models.FloatField(default=0)),
                ('quant_pago_gotas', models.FloatField(default=0)),
                ('quant_integracao_gotas', models.FloatField(default=0)),
                ('valor_total_bonificado', models.FloatField(default=0)),
                ('valor_total_gerencial', models.FloatField(default=0)),
                ('valor_total_pago', models.FloatField(default=0)),
                ('valor_total_pago_gotas', models.FloatField(default=0)),
                ('valor_total_integracao_gotas', models.FloatField(default=0)),
                ('fixo', models.FloatField(default=0)),
                ('desconto', models.FloatField(default=0)),
                ('descricao_desconto', models.TextField(default=0)),
                ('cobrado_total', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Ordem_servico',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_os', models.IntegerField(default=0)),
                ('data_hora', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Posto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50)),
                ('razao_social', models.CharField(max_length=100)),
                ('cnpj', models.CharField(max_length=100)),
                ('inscrisao_municipal', models.CharField(max_length=100)),
                ('inscrisao_estadual', models.CharField(max_length=100)),
                ('cep', models.CharField(max_length=100)),
                ('endereco', models.CharField(max_length=100)),
                ('cidade', models.CharField(max_length=100)),
                ('bairro', models.CharField(max_length=100)),
                ('estado', models.CharField(max_length=100)),
                ('nome_responsavel', models.CharField(max_length=100)),
                ('email', models.CharField(max_length=100)),
                ('telefone', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Produto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('nome_display', models.CharField(blank=True, max_length=100, null=True)),
                ('codigo_equipamento', models.IntegerField(blank=True, null=True)),
                ('status', models.BooleanField()),
                ('data_instalacao', models.DateField(default=datetime.date.today)),
                ('control_use', models.CharField(max_length=100)),
                ('codigo_primario', models.IntegerField(default=0)),
                ('condigo_secundario', models.IntegerField(default=0)),
                ('posto_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Posto')),
            ],
        ),
        migrations.CreateModel(
            name='Rede_cliente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(blank=True, max_length=100, null=True)),
                ('matriz', models.IntegerField(blank=True, default=0, null=True)),
                ('produto', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.Produto')),
            ],
        ),
        migrations.CreateModel(
            name='Tipo_produto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('codigo_equipamento', models.IntegerField(default=0)),
                ('descricao', models.CharField(max_length=100)),
                ('corpo_email', models.TextField()),
                ('produto_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.Produto')),
            ],
        ),
        migrations.CreateModel(
            name='Type_billing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('venda', models.BooleanField()),
                ('moedeiro_encerrante', models.FloatField(default=0)),
                ('pago', models.FloatField(default=0)),
                ('bonificado', models.FloatField(default=0)),
                ('gerencial', models.FloatField(default=0)),
                ('pago_gotas', models.FloatField(default=0)),
                ('integracao_gotas', models.FloatField(default=0)),
                ('maximo', models.FloatField(default=0)),
                ('minimo', models.FloatField(default=0)),
                ('chave', models.CharField(max_length=100)),
                ('fixo', models.FloatField(default=0)),
                ('fixo_variavel', models.FloatField(default=0)),
                ('data_atualizacao', models.DateField(default=datetime.date.today)),
                ('data_ultima_atualizacao', models.DateField(default=datetime.date.today)),
                ('nome_financeiro', models.CharField(max_length=100)),
                ('descricao', models.CharField(max_length=100)),
                ('email_cobranca', models.CharField(max_length=200)),
                ('produto_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.Produto')),
            ],
        ),
        migrations.AddField(
            model_name='ordem_servico',
            name='produto_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Produto'),
        ),
        migrations.AddField(
            model_name='billing',
            name='produto_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Produto'),
        ),
    ]
