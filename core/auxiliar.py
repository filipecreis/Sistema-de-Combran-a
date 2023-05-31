from .models import  Billing, Posto, Tipo_produto, Produto
from datetime import datetime
from django.db.models import Sum
import requests
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta


def checar_atualizacao(proxima_atualizacao, status_produto):
   
    # inicializa as variáveis com valores padrão
    data_proxima_atualizacao = None
    atualizar = False
    id_typebilling = None
    
    # verifica se a próxima atualização existe e se a venda está desativada (0)
    if proxima_atualizacao and not proxima_atualizacao.venda and status_produto:
        data_proxima_atualizacao = proxima_atualizacao.data_atualizacao
        # verifica se a data da próxima atualização já passou
        if data_proxima_atualizacao <= datetime.utcnow().date():
            atualizar = True
            id_typebilling = proxima_atualizacao.id
    
    return data_proxima_atualizacao, atualizar, id_typebilling


def total_cobrado(produto_id):
    
    try:
        total_cobrado = Billing.objects.filter(produto_id=produto_id).exclude(status=0).aggregate(total=Sum('cobrado_total'))['total']
        return total_cobrado if total_cobrado else 0
    except Exception as e:
        print("Erro: ", e)
        return 0


def ipca_acumulado():

    # Acessar API do Banco Central para a série temporal do IPCA 12 últimos meses(código 433) 
    url = 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados/ultimos/12?formato=json'
    response = requests.get(url)
    data = response.json()

    # Converter para DataFrame e processar
    df = pd.DataFrame(data)
    df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
    df['valor'] = pd.to_numeric(df['valor']) / 100  # Convertendo para taxa decimal

    # Converter a taxa de inflação mensal para uma base de (1 + taxa)
    df['valor'] = 1 + df['valor']

    # Calcular a inflação acumulada como o produto das taxas mensais
    inflacao_acumulada = df['valor'].prod() - 1

    # Converter de volta para uma taxa percentual
    inflacao_acumulada = inflacao_acumulada * 100

    return (inflacao_acumulada)


def texto_email(dados_cobranca):
    
    dados_produto = dados_cobranca.produto_id
    dados_posto = dados_produto.posto_id
    tipo_produto = dados_produto.tipo_produto_id
    
    # Obtem as duas primeiras cobranças para o produto específico, excluindo as de status 0, e ordenadas por ID
    cobrancas = Billing.objects.filter(produto_id=dados_cobranca.produto_id).exclude(status=0).order_by('-id')[:2]

    if(cobrancas[0]):
        ultimo_encerrante = cobrancas[0].encerrante
    else:
        ultimo_encerrante = 0
        
    if(cobrancas[1]):
        penultimo_encerrante = cobrancas[1].encerrante
    else:
        penultimo_encerrante = 0
    
    lista_palavras_chave =[]
    
    lista_palavras_chave = ["{posto}","{nome_financeiro}","{mes_atual}","{mes_anterior}","{produto}",
                            "{moedeiro_v}","{pago_v}","{bonificado_v}","{gerencial_v}", "{gotas_v}","{gotas_integrada_v}",
                            "{moedeiro_q}","{pago_q}","{bonificado_q}","{gerencial_q}","{gotas_q}","{gotas_integrada_q}",
                            "{moedeiro_t}","{pago_t}","{bonificado_t}","{gerencial_t}","{gotas_t}","{gotas_integrada_t}",
                            "{fixo_variavel}", "{fixo}", "{desconto}",
                            "{vencimento_boleto}","{valor_boleto}","{total_vaucher}"]
    
    
    posto = dados_posto.nome
    nome_financeiro = dados_cobranca.nome_financeiro
    mes_atual = datetime.now().strftime("%m-%Y")
    mes_anterior = (datetime.now() - relativedelta(months=1)).strftime("%m-%Y")
    produto = tipo_produto.nome
    moedeiro_v = dados_cobranca.moedeiro_encerrante
    pago_v = dados_cobranca.pago
    bonificado_v = dados_cobranca.bonificado
    gerencial_v = dados_cobranca.gerencial
    gotas_v = dados_cobranca.pago_gotas
    gotas_integrada_v = dados_cobranca.integracao_gotas
    moedeiro_q = (ultimo_encerrante - penultimo_encerrante)
    pago_q = cobrancas[0].quant_pago
    bonificado_q = cobrancas[0].quant_bonificado
    gerencial_q = cobrancas[0].quant_gerencial
    gotas_q = cobrancas[0].quant_pago_gotas
    gotas_integrada_q = cobrancas[0].quant_integracao_gotas
    moedeiro_t = moedeiro_q * moedeiro_v
    pago_t = pago_q * pago_v
    bonificado_t = bonificado_q * bonificado_v
    gerencial_t = gerencial_q*gerencial_v
    gotas_t = gotas_q * gotas_v
    gotas_integrada_t = gotas_integrada_q * gotas_integrada_v
    fixo_variavel_c = cobrancas[0].fixo_variavel
    fixo = cobrancas[0].fixo
    desconto = cobrancas[0].desconto
    vencimento_boleto = cobrancas[0].pay_date.strftime("%d/%m/%Y")
    valor_boleto = cobrancas[0].cobrado_total
    total_vaucher = pago_q + bonificado_q + gerencial_q + gotas_q + gotas_integrada_q
    
    valor_variaveis = [ ]
    
    valor_variaveis = [
    str(posto),
    str(nome_financeiro),
    str(mes_atual),
    str(mes_anterior),
    str(produto),
    str(moedeiro_v),
    str(pago_v),
    str(bonificado_v),
    str(gerencial_v),
    str(gotas_v),
    str(gotas_integrada_v),
    str(moedeiro_q),
    str(pago_q),
    str(bonificado_q),
    str(gerencial_q),
    str(gotas_q),
    str(gotas_integrada_q),
    str(moedeiro_t),
    str(pago_t),
    str(bonificado_t),
    str(gerencial_t),
    str(gotas_t),
    str(gotas_integrada_t),
    str(fixo_variavel_c),
    str(fixo),
    str(desconto),
    str(vencimento_boleto),
    str(valor_boleto),
    str(total_vaucher),
]

    texto_email = dados_cobranca.corpo_email
    
    for i in range(len(lista_palavras_chave)):
        texto_email = texto_email.replace(lista_palavras_chave[i], valor_variaveis[i])

    total =  moedeiro_t + pago_t + bonificado_t + gerencial_t + gotas_t + gotas_integrada_t
    

    if(total > dados_cobranca.maximo and dados_cobranca.maximo!=0):
        texto_email = texto_email.replace("{msg_max_min}", "Vale ressaltar que o valor calculado excedeu o valor máximo estabelecido em nosso contrato." )
    elif(total < dados_cobranca.minimo):
        total = dados_cobranca.minimo
        texto_email = texto_email.replace("{msg_max_min}","Vale ressaltar que o valor calculado não excede o valor mínimo estabelecido em nosso contrato.")
    else:
        texto_email = texto_email.replace("{msg_max_min}","")
    
    if(desconto):
        texto_email = texto_email.replace("{desconto}","Desconto Concedido: R$ " + str(desconto))
    else:
        texto_email = texto_email.replace("{desconto}","")
    
    return texto_email
