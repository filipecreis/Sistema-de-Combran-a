import requests
import json
import time
from .models import Posto

TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHAiOiJkZTA3MGYwZTc4YmVhYmM2MzlkZTYzNGRjNjE2ZGIzNiIsInN1YmRvbWluaW8iOiJydGlzb2x1dGlvbnMiLCJjbGllbnQiOiI2Nzc4ODZjMTQ3ZGVkYjViNzkyNjNmY2E1M2QzMzVmNTNkNWE0ZjczIiwiY3JlYXRlZCI6MTY4NTk5ODIxOX0=.M9q9xr2hSgacs7gcwxfaTsm5T760G5f8AStClAg7r2g='
URL_TOKEN = 'https://api.egestor.com.br/api/oauth/access_token'

def make_request(url, method='POST', headers=None, data=None):
    response = requests.request(method, url, headers=headers, data=json.dumps(data))
    response.raise_for_status()  # Raises an exception if the response contains an HTTP error status code
    return response.json()

def get_personal_token():
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "grant_type": "personal",
        "personal_token": TOKEN
    }
    
    response_data = make_request(URL_TOKEN, headers=headers, data=data)
    return response_data.get('access_token')

def baixar_banco_dados_posto():
    
    # Get personal token
    personal_token = get_personal_token()

    # Define headers for GET request
    headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {personal_token}'
    }
    """
    # URL to make a GET request
    url = 'https://api.egestor.com.br/api/v1/contatos/?clienteFinal=1'

    all_data = []

    while url:
        response_data = make_request(url, method='GET', headers=headers)
        all_data.extend(response_data.get('data', []))
        url = response_data.get('next_page_url')

    # Extraia 'codigo' de cada dicionário
    codigos = [d['codigo'] for d in all_data]

    # Salva os dados em um arquivo .txt
    with open('codigos.txt', 'w') as outfile:
        json.dump(codigos, outfile)
    
    # Agora 'codigos' é uma lista de todos os valores 'codigo'
    print(len(codigos))

"""
    s = '1101, 1102, 1103, 1104, 1105, 1106, 1107, 1108, 1109, 1110, 1111, 1112, 1113, 1114, 1115, 1116, 1117, 1118, 1119, 1120, 1121, 1122, 1123, 1124, 1125, 1126, 1127, 1128, 1130, 1131, 1132, 1133, 1134, 1135, 1136, 1137, 1140, 1141, 1142, 1143, 1144, 1145, 1146, 1149, 1150, 1151, 1152, 1153, 1155, 1156, 1157, 1158, 1159, 1160, 1161, 1162, 1163, 1164, 1165, 1166, 1167, 1168, 1171, 1172, 1174, 1175, 1177, 1178, 1179, 1180, 1181, 1182, 1183, 1184, 1185, 1186'
    lista = [int(i) for i in s.split(', ')]
    
    # Endereço base da URL
    base_url = 'https://private-anon-73a021a6d6-egestor.apiary-proxy.com/api/v1/contatos/'

    # Itera sobre a lista de códigos
    for codigo in lista:
        # Cria a URL completa adicionando o código ao endereço base
        url = base_url + str(codigo)
        
        espera = 3
        attempts = True
        # Faça a requisição
        while attempts:
            try:
                response_data = make_request(url, method='GET', headers=headers)
                if response_data.get('codigo') == codigo:
                    print(f"Dados obtidos com sucesso para o código {codigo}")

                    # Instancia um novo objeto Posto
                    posto = Posto(
                        nome=response_data['nome'],
                        razao_social=response_data['fantasia'],
                        cnpj=response_data['cpfcnpj'],
                        inscrisao_municipal=response_data['inscricaoMunicipal'],
                        inscrisao_estadual=response_data['inscricaoEstadual'],
                        cep = response_data['cep'],
                        endereco = response_data['logradouro'] + ', ' + str(response_data['numero']),
                        cidade=response_data['cidade'],
                        bairro=response_data['bairro'],
                        estado=response_data['uf'],
                        nome_responsavel=response_data['nomeParaContato'],
                        email_responsavel=', '.join(response_data['emails']),  # Junta todos os e-mails com ', ' entre eles
                        telefone_responsavel=', '.join(response_data['fones']),  # Junta todos os telefones com ', ' entre eles
                        id_egestor = codigo
                    )

                    # Salva o objeto no banco de dados
                    posto.save()

                    attempts = False
                    # Sai do loop, pois os dados foram obtidos com sucesso
            except Exception as e:
                print(f"Erro ao fazer requisição para o código {codigo}: {e}")
                # Adiciona um atraso antes da próxima tentativa (em segundos)
                time.sleep(espera)
                espera += 1
        
        
        # Adiciona um atraso antes de fazer a requisição para o próximo código (em segundos)
        time.sleep(1)
