import requests
import json


url = 'https://api.egestor.com.br/api/oauth/access_token'
headers = {'Content-Type': 'application/json'}
data = {
"grant_type": "personal",
"personal_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHAiOiJkZTA3MGYwZTc4YmVhYmM2MzlkZTYzNGRjNjE2ZGIzNiIsInN1YmRvbWluaW8iOiJydGlzb2x1dGlvbnMiLCJjbGllbnQiOiI2Nzc4ODZjMTQ3ZGVkYjViNzkyNjNmY2E1M2QzMzVmNTNkNWE0ZjczIiwiY3JlYXRlZCI6MTY4NTk5ODIxOX0=.M9q9xr2hSgacs7gcwxfaTsm5T760G5f8AStClAg7r2g="
}

response = requests.post(url, headers=headers, data=json.dumps(data))

if response.status_code == 200:
    response_data = response.json()
    access_token = response_data.get('access_token')
    access_token
else:
    print(f'Erro na solicitação: {response.status_code}, {response.text}')



url = 'https://private-anon-454a7fd7a7-egestor.apiary-proxy.com/api/v1/recebimentos'
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + access_token  # Substitua pelo seu token de acesso
}
data = {
    "codPlanoContas": 45,          #Produto 45 = Moedeiro; 12 = SmartShower; 74 = SmartShower WiFi
								   #73 = Moedeiro Smart; 75 = Gotas COntrol; 76 = MiniSmart; 46 = Suporte Online
    "codFormaPgto": 3,             #Boleto = 3
    "descricao": "teste filipe",   #Titulo
    "valor": 200.91,               #Valor a cobrar
    "dtVenc": "2023-06-10",		   #Data Vencimento 5D
	"dtCred": "2023-06-11",        #Data do Credito Previsao 5d+1
    "dtComp": "2023-06-07",		   #Data Atual
    "recebido": False,             #Sempre false
    "codContato": 1,               #Cliente
    "codDisponivel": 1,            #Plano de Contas  1 = Itau
    "obs": "",					   #Desconto
    "tags": [					   #Tags
        "Filipe"]
}

response = requests.post(url, headers=headers, data=json.dumps(data))

if response.status_code == 200:
    codRecebimentos = response.json()['codigo']
    print(codRecebimentos)
else:
    print("Erro na solicitação:", response.status_code)


values = {
    "codContato": 1,
    "dtVenc": "2023-06-10",
    "codRecebimentos": 
    [
        codRecebimentos
    ]
}

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + access_token
}

response = requests.post('https://api.egestor.com.br/api/v1/boletos', json=values, headers=headers)

print(response.text)

if response.status_code == 200:
    # A solicitação foi bem-sucedida
    response_data = response.json()
    print('Response:')
    print(response_data)

    # Extrai o link do arquivo PDF
    pdf_url = response_data.get('link')
    
    # Faz o download do arquivo PDF
    if pdf_url:
        pdf_response = requests.get(pdf_url)
        if pdf_response.status_code == 200:
            # Salva o arquivo PDF localmente
            pdf_path = 'boleto.pdf'  # Caminho do arquivo PDF
            with open(pdf_path, 'wb') as f:
                f.write(pdf_response.content)
            print('Arquivo PDF baixado com sucesso.')
            print(pdf_path)
        else:
            print('Erro ao baixar o arquivo PDF.')
    else:
        print('Nenhum link de arquivo PDF encontrado na resposta.')
else:
    # A solicitação falhou
    print('Erro na solicitação. Código de resposta:', response.status_code)


import requests
import json


def personal_token():
    
    url = 'https://api.egestor.com.br/api/oauth/access_token'
    headers = {'Content-Type': 'application/json'}
    data = {
    "grant_type": "personal",
    "personal_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHAiOiJkZTA3MGYwZTc4YmVhYmM2MzlkZTYzNGRjNjE2ZGIzNiIsInN1YmRvbWluaW8iOiJydGlzb2x1dGlvbnMiLCJjbGllbnQiOiI2Nzc4ODZjMTQ3ZGVkYjViNzkyNjNmY2E1M2QzMzVmNTNkNWE0ZjczIiwiY3JlYXRlZCI6MTY4NTk5ODIxOX0=.M9q9xr2hSgacs7gcwxfaTsm5T760G5f8AStClAg7r2g="
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_data = response.json()
        return response_data.get('access_token')
        
    else:
        print(f'Erro na solicitação: {response.status_code}, {response.text}')


def gerar_cobranca(access_token, ):
    
    url = 'https://private-anon-454a7fd7a7-egestor.apiary-proxy.com/api/v1/recebimentos'
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token  # Token de acesso
    }
    
    data = {
        "codPlanoContas": 45,          #Produto 45 = Moedeiro; 12 = SmartShower; 74 = SmartShower WiFi
                                       #73 = Moedeiro Smart; 75 = Gotas COntrol; 76 = MiniSmart; 46 = Suporte Online
        "codFormaPgto": 3,             #Boleto = 3, por padrão boleto
        "descricao": "teste123",	   #Titulo
        "valor": 9.91,                 #Valor a cobrar
        "dtVenc": "2023-06-10",		   #Data Vencimento 5D
        "dtCred": "2023-06-11",        #Data do Credito Previsao 5d+1
        "dtComp": "2023-06-06",		   #Data Atual
        "recebido": False,             #Sempre false
        "codContato": 1,               #Cliente
        "codDisponivel": 1,            #Plano de Contas  1 = Itau, por padrão itau
        "obs": "",					   #Desconto, quando tiver desconto
        "tags": [					   #Tags
            "Filipe"]
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        codRecebimentos = response.json()['codigo']
        print(codRecebimentos)
    else:
        print("Erro na solicitação:", response.status_code)
    

def gerar_boleto(access_token):

    url = 'https://api.egestor.com.br/api/v1/boletos'
    
    values = {
        "codContato": 1,
        "dtVenc": "2023-06-30",
        "codRecebimentos": [
            '3356'
        ]
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
    }

    response = requests.post(url, json=values, headers=headers)

    print(response.text)

    if response.status_code == 200:
        # A solicitação foi bem-sucedida
        response_data = response.json()
        print('Response:')
        print(response_data)

        # Extrai o link do arquivo PDF
        pdf_url = response_data.get('link')
        
        # Faz o download do arquivo PDF
        if pdf_url:
            pdf_response = requests.get(pdf_url)
            if pdf_response.status_code == 200:
                # Salva o arquivo PDF localmente
                pdf_path = 'boleto.pdf'  # Caminho do arquivo PDF
                with open(pdf_path, 'wb') as f:
                    f.write(pdf_response.content)
                print('Arquivo PDF baixado com sucesso.')
                print(pdf_path)
            else:
                print('Erro ao baixar o arquivo PDF.')
        else:
            print('Nenhum link de arquivo PDF encontrado na resposta.')
    else:
        # A solicitação falhou
        print('Erro na solicitação. Código de resposta:', response.status_code)

