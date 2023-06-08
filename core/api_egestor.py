import requests
import json
import os
from datetime import date


# Constantes
TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHAiOiJkZTA3MGYwZTc4YmVhYmM2MzlkZTYzNGRjNjE2ZGIzNiIsInN1YmRvbWluaW8iOiJydGlzb2x1dGlvbnMiLCJjbGllbnQiOiI2Nzc4ODZjMTQ3ZGVkYjViNzkyNjNmY2E1M2QzMzVmNTNkNWE0ZjczIiwiY3JlYXRlZCI6MTY4NTk5ODIxOX0=.M9q9xr2hSgacs7gcwxfaTsm5T760G5f8AStClAg7r2g='
URL_TOKEN = 'https://api.egestor.com.br/api/oauth/access_token'
URL_COBRANCA = 'https://private-anon-454a7fd7a7-egestor.apiary-proxy.com/api/v1/recebimentos'
URL_BOLETO = 'https://api.egestor.com.br/api/v1/boletos'
URL_RECIBO = 'http://rtisolutions.com.br/acesso_cliente/usuario/receipt.php'

# Conta quantos arquivos tem no diretório
def contar_arquivos(diretorio):
    return len(os.listdir(diretorio)) + 1

# Funções auxiliares
def make_request(url, method='POST', headers=None, data=None):
    response = requests.request(method, url, headers=headers, data=json.dumps(data))
    response.raise_for_status()  # Levanta uma exceção se a resposta contém um código de status de erro HTTP
    return response.json()


def get_personal_token():
    headers = {'Content-Type': 'application/json'}
    
    data = {
        "grant_type": "personal",
        "personal_token": TOKEN
    }

    response_data = make_request(URL_TOKEN, headers=headers, data=data)
    return response_data.get('access_token')


def gerar_cobranca(access_token, codPlanoContas, descricao, valor, dtVenc, dtCred, codContato, produto):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'  
    }
    
    # Dados da cobrança
    data = {
        "codPlanoContas": codPlanoContas,               #Produto 45 = Moedeiro; 12 = SmartShower; 74 = SmartShower WiFi 73 = Moedeiro Smart; 75 = Gotas COntrol; 76 = MiniSmart; 46 = Suporte Online
        "codFormaPgto": 3,                              #Boleto = 3, por padrão boleto
        "descricao": descricao,	                        #Titulo
        "valor": valor,                                 #Valor a cobrar
        "dtVenc": dtVenc,		                        #Data Vencimento 5D
        "dtCred": dtCred,                               #Data do Credito Previsao 5d+1
        "dtComp": date.today().strftime("%Y-%m-%d"),    #Data Atual
        "recebido": False,                              #Sempre false
        "codContato": codContato,                       #Cliente
        "codDisponivel": 1,                             #Plano de Contas  1 = Itau, por padrão itau
        "obs": "",					                    #Desconto, quando tiver desconto
        "tags": [					                    #Tags
            produto]
    }

    response_data = make_request(URL_COBRANCA, headers=headers, data=data)
    return response_data['codigo']


def gerar_boleto(access_token,codContato, dtVenc, codRecebimentos):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    
    values = {
        "codContato": codContato,
        "dtVenc": dtVenc,
        "codRecebimentos": [ 
            codRecebimentos
        ]
    }

    response_data = make_request(URL_BOLETO, method='POST', headers=headers, data=values)
    
    return response_data.get('link')


def baixar_boleto(pdf_url, nome_boleto, deretorio):
    # Faz o download do arquivo PDF
    if pdf_url:
        pdf_response = requests.get(pdf_url)
        if pdf_response.status_code == 200:
            # Cria a pasta "estado/produto/posto" se ela não existir
            pasta = f'C:/Users/USER/Desktop/Pasta_teste/{deretorio}' # Precisa colocar de acordo com o computador ver oq pode fazer para ser acessível em qualquer computador
            os.makedirs(pasta, exist_ok=True)
            
            # Salva o arquivo PDF localmente
            numero_pdf = contar_arquivos(pasta)
            pdf_path = f'{pasta}/{nome_boleto}-{numero_pdf}.pdf'  # Caminho do arquivo PDF
            
            with open(pdf_path, 'wb') as f:
                f.write(pdf_response.content)
            print('Arquivo PDF baixado com sucesso.')
            return pdf_path
        else:
            print('Erro ao baixar o arquivo PDF.')
    else:
        print('Nenhum link de arquivo PDF encontrado na resposta.')


def recibo(posto, cnpj, valor, produto):

    url = URL_RECIBO
    params = {
        "client": posto,
        "cnpj": cnpj,
        "value": valor,
        "product": produto
    }

    response = requests.get(url, params=params)

    # Define o caminho para a pasta de downloads
    download_folder = "C:/Users/USER/Downloads/"

    # Define o caminho completo para o arquivo
    file_path = download_folder + 'receipt.pdf'

    with open(file_path, 'wb') as f:
        f.write(response.content)
    
    return file_path
    

def cobranca_boleto(codPlanoContas, descricao, valor, dtVenc, dtCred, codContato, deretorio, nome_boleto,posto, cnpj, produto):
    
    try:
        access_token = get_personal_token()
        codRecebimentos = gerar_cobranca(access_token, codPlanoContas, descricao, valor, dtVenc, dtCred, codContato, produto)
        pdf_url = gerar_boleto(access_token,codContato, dtVenc, codRecebimentos)
        direto_boleto = baixar_boleto(pdf_url, nome_boleto, deretorio)
        diretorio_recibo = recibo(posto, cnpj, valor, produto)
        return diretorio_recibo, direto_boleto
    
    except requests.HTTPError as err:
        print(f"Erro na solicitação: {err.response.status_code}, {err.response.text}")
