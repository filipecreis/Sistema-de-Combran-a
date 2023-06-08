from .models import  Billing
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
