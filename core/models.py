from django.db import models
from datetime import date, timedelta

ESTADOS_BRASILEIROS = [
    'Acre',
    'Alagoas',
    'Amapá',
    'Amazonas',
    'Bahia',
    'Ceará',
    'Distrito Federal',
    'Espírito Santo',
    'Goiás',
    'Maranhão',
    'Mato Grosso',
    'Mato Grosso do Sul',
    'Minas Gerais',
    'Pará',
    'Paraíba',
    'Paraná',
    'Pernambuco',
    'Piauí',
    'Rio de Janeiro',
    'Rio Grande do Norte',
    'Rio Grande do Sul',
    'Rondônia',
    'Roraima',
    'Santa Catarina',
    'São Paulo',
    'Sergipe',
    'Tocantins',
]

CORPO_EMAIL = """
Prezado {nome_financeiro},

Espero que esteja bem.

Venho por meio deste email apresentar a você os detalhes da cobrança referentes à locação do nosso sistema de controle, {produto}, que está instalado no {posto}.

Em anexo, você encontrará os seguintes documentos:

Boleto de Faturamento - {mes_anterior}
Recibo de Locação - {mes_anterior}
Gostaria de fornecer um breve resumo dos dados para sua apreciação:

Período: {mes_anterior}

Total de Vouchers Comprados: {total_vaucher}
Banhos Moedeiro: {moedeiro_q}
Banhos Pago: {pago_q}
Banhos Bonificado: {bonificado_q}
Banhos Gerencial: {gerencial_q}
Banhos Gotas: {gotas_q}
Banhos Gotas Integrado: {gotas_integrada_q}

Valor por Voucher: 
Moedeiro: R$ {moedeiro_v}
Banhos Pago: R$ {pago_v}
Banhos Bonificado: R$ {bonificado_v}
Banhos Gerencial: R$ {gerencial_v}
Banhos Gotas: R$ {gotas_v}
Banhos Gotas Integrado: R$ {gotas_integrada_v}

A seguir, apresento o cálculo que originou o valor do boleto:

Banhos Moedeiro: {moedeiro_q} vouchers x R$ {moedeiro_v} = R$ {moedeiro_t}
Banhos Pagos: {pago_q} vouchers x R$ {pago_v} = R$ {pago_t}
Banhos Bonificados: {bonificado_q} vouchers x R$ {bonificado_q} = R$ {bonificado_t}
Banhos Gerencial: {gerencial_q} vouchers x R$ {gerencial_v} = R$ {gerencial_t}
Banhos Gotas: {gotas_q} vouchers x R$ {gotas_v} = R$ {gotas_t}
Banhos Gotas Integrado: {gotas_integrada_q} vouchers x R$ {gotas_integrada_v} = R$ {gotas_integrada_t}
{desconto}

{msg_max_min}

Assim, o valor total do boleto é R$ {valor_boleto}, com vencimento previsto para {vencimento_boleto}.

Agradecemos antecipadamente pela atenção e solicitamos a gentileza de confirmar o recebimento deste e-mail.

Atenciosamente,
    """

def pay_date_f():
    return date.today() + timedelta(days=5)

def proxima_atualizacao():
    return date.today() + timedelta(days=365)

class Rede_cliente(models.Model):
    nome = models.CharField(max_length = 100, blank=True, null= True)
    matriz = models.IntegerField(blank = True, null=True, default=0)

    def __str__(self):
        return self.nome

class Posto(models.Model):
    
    ESTADO_CHOICES = [(estado, estado) for estado in ESTADOS_BRASILEIROS]
    
    nome = models.CharField(max_length = 50, blank=False, null=False)
    razao_social = models.CharField(max_length = 100, blank=False, null=False)
    cnpj = models.CharField(max_length = 100, blank=False, null= False)
    inscrisao_municipal = models.CharField(max_length = 100, blank=False, null=False)
    inscrisao_estadual = models.CharField(max_length = 100, blank=False, null=False)
    cep = models.CharField(max_length = 100, blank=False, null=False)
    endereco = models.CharField(max_length = 100, blank=False, null=False)
    cidade = models.CharField(max_length = 100, blank=False, null=False)
    bairro = models.CharField(max_length = 100, blank=False, null=False)
    estado = models.CharField(max_length=20, blank=False, null=False) #choices=ESTADO_CHOICES
    nome_responsavel = models.CharField(max_length = 100, blank=False, null=False)
    email_responsavel = models.CharField(max_length = 100, blank=False, null=False)
    telefone_responsavel = models.CharField(max_length = 100, blank=False, null=False)
    id_egestor = models.IntegerField(blank=False, null=False)
    rede_id = models.ForeignKey(Rede_cliente, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return self.nome

class Tipo_produto(models.Model):
    nome = models.CharField(max_length = 100, blank=False, null= False)
    codigo_egestor = models.IntegerField(blank=False, null=False, default=0)
    
    def __str__(self):
        return self.nome

class Produto(models.Model):
    
    STATUS_CHOICES = [
    (True, 'Ativo'),
    (False, 'Desativado'),
    ]
    nome = models.CharField(max_length=100)
    nome_display = models.CharField(max_length=100, blank=True, null=True)
    codigo_equipamento = models.IntegerField(blank=True, null=True)
    status = models.BooleanField(choices=STATUS_CHOICES)
    data_instalacao = models.DateField(default=date.today)
    control_use = models.CharField(max_length=100)
    codigo_primario = models.IntegerField(default=0)
    condigo_secundario = models.IntegerField(default=0)
    posto_id = models.ForeignKey(Posto, on_delete=models.CASCADE)
    tipo_produto_id = models.ForeignKey(Tipo_produto, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nome


class Billing(models.Model):
    STATUS_CHOICES = [
        (0, 'Cancelado'),
        (1, 'Cobrança realizada'),
        (2, 'Pagamento efetuado'),
    ]
    status = models.IntegerField(choices=STATUS_CHOICES)
    invoice_date = models.DateField(default=date.today)
    pay_date = models.DateField(default=pay_date_f)
    encerrante = models.IntegerField(default=0)
    quant_bonificado = models.FloatField(default=0)
    quant_gerencial = models.FloatField(default=0)
    quant_pago = models.FloatField(default=0)
    quant_pago_gotas = models.FloatField(default=0)
    quant_integracao_gotas = models.FloatField(default=0)
    fixo = models.FloatField(default=0)
    fixo_variavel = models.FloatField(default=0) ## novo
    desconto = models.FloatField(default=0)
    descricao_desconto = models.TextField(default=0, blank=True, null=True)
    cobrado_total = models.FloatField(default=0)
    produto_id = models.ForeignKey(Produto, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.produto_id.nome)
    

class Type_billing(models.Model):
    venda = models.FloatField(blank=False, null=False,default=0)
    parcela_venda = models.FloatField(default=0, blank=False, null=False)
    moedeiro_encerrante = models.FloatField(default=0, blank=False, null=False)
    pago = models.FloatField(default=0, blank=False, null=False)
    bonificado = models.FloatField(default=0, blank=False, null=False)
    gerencial = models.FloatField(default=0, blank=False, null=False)
    pago_gotas = models.FloatField(default=0, blank=False, null=False)
    integracao_gotas = models.FloatField(default=0, blank=False, null=False)
    maximo = models.FloatField(default=0, blank=False, null=False)
    minimo = models.FloatField(default=0, blank=False, null=False)
    fixo = models.FloatField(default=0, blank=False, null=False)
    fixo_variavel = models.FloatField(default=0, blank=False, null=False)
    data_atualizacao = models.DateField(default=proxima_atualizacao)
    data_ultima_atualizacao = models.DateField(default=date.today)
    contrato = models.TextField(default="0", blank=False, null=False)
    nome_financeiro = models.CharField(max_length=100, blank=False, null=False)
    email_cobranca = models.CharField(max_length = 100, blank=False, null=False, default="0")
    corpo_email = models.TextField(default=CORPO_EMAIL, blank=False, null=False)
    telefone_cobranca = models.CharField(max_length = 100, blank=False, null=False, default="0")
    produto_id = models.OneToOneField(Produto, on_delete=models.CASCADE)
    
    def __str__(self):
        return str(self.produto_id.nome)


class Ordem_servico(models.Model):
    numero_os = models.IntegerField(blank=False, null=False, default=0)
    data_hora = models.DateTimeField()
    produto_id = models.ForeignKey(Produto, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.data_hora
