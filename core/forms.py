from django.forms import ModelForm
from .models import Posto, Produto, Tipo_produto, Type_billing, Billing
from django import forms

"""
class TipoProdutoForm(forms.ModelForm):
    produto = forms.ModelChoiceField(queryset=Produto.objects.all(), widget=forms.HiddenInput())

    class Meta:
        model = Tipo_produto
        fields = ['nome', 'codigo_equipamento']


class TyeBillingForm(forms.ModelForm):
    produto = forms.ModelChoiceField(queryset=Produto.objects.all(), widget=forms.HiddenInput())

    class Meta:
        model = Type_billing
        fields = ['pago', 'bonificado', 'fixo', 'gerencial', 'maximo', 'minimo', 'logica_cobranca', 'chave', 'data_atualizacao', 'produto']


class PostoForm(ModelForm):
    class Meta:
        model = Posto
        fields = '__all__'



class ProdutoForm(ModelForm):
    class Meta:
        model = Produto
        fields = ('nome', 'status', 'data_instalacao', 'codigo_primario', 'condigo_secundario')
"""

class BillingStatusForm(forms.ModelForm):
    class Meta:
        model = Billing
        fields = ['status']


class Atualizacao(forms.ModelForm):
    class Meta:
        model = Type_billing
        fields = ['pago', 'bonificado', 'gerencial', 'pago_gotas',
                  'integracao_gotas', 'fixo_variavel', 'fixo', 'maximo',
                  'minimo', 'data_atualizacao', 'data_ultima_atualizacao']
    

class BillingVendaFixaForm(forms.ModelForm):
    
    cobrado_total = forms.FloatField(widget=forms.NumberInput(
        attrs={'readonly': True}))
    
    class Meta:
        model = Billing
        fields = ['invoice_date',
                  'pay_date',
                  'desconto',
                  'descricao_desconto',
                  'cobrado_total']
        

class BillingForm(forms.ModelForm):
    class Meta:
        model = Billing
        fields = ['invoice_date',
                  'pay_date',
                  'encerrante',
                  'quant_bonificado',
                  'quant_gerencial',
                  'quant_pago',
                  'quant_pago_gotas',
                  'quant_integracao_gotas',
                  'desconto',
                  'descricao_desconto',
                  'cobrado_total'
                  ]
