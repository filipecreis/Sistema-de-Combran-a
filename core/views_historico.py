from django.shortcuts import render, redirect, get_object_or_404
from .models import Produto, Type_billing, Billing
from .forms import BillingStatusForm, Atualizacao
from .auxiliar import checar_atualizacao, ipca_acumulado
from django.views.decorators.http import require_GET, require_http_methods
from django.http import JsonResponse

# Essa função é responsável por buscar a lista de produtos com o seu histórico de cobrança.
def produtos_historico_cobranca(request):

    # Inicializa uma lista vazia para armazenar os dados dos produtos a serem retornados.
    produtos_list = []
    
    # Obtém o valor do parâmetro 'search' da URL. Se não houver tal parâmetro, utiliza uma string vazia.
    search_query = request.GET.get('search', '')

    # Se houver um valor para 'search', filtra os produtos cujo nome do posto associado contém o valor de 'search' 
    # (não sensível a maiúsculas e minúsculas). Caso contrário, obtém todos os produtos.
    if search_query:
        produtos = Produto.objects.filter(posto_id__nome__icontains=search_query)
    else:
        produtos = Produto.objects.all()
    
    # Ordena os produtos por status em ordem decrescente. Utiliza 'prefetch_related' para otimizar as consultas 
    # relacionadas a 'billing_set' e 'type_billing'.
    produtos = produtos.order_by('-status').prefetch_related('billing_set', 'type_billing')

    # Para cada produto na lista de produtos...
    for prod in produtos:
        # Atribui o nome do posto associado ao produto.
        posto_relacionado = prod.posto_id.nome
        # Atribui a rede do posto associado ao produto.
        rede_posto = prod.posto_id.rede_id
        # Busca a última cobrança associada ao produto, ordenadas pela data da fatura.
        ultima_cobranca = prod.billing_set.order_by('-invoice_date').first()
        # Atribui o tipo de cobrança associado ao produto.
        proxima_atualizacao = prod.type_billing
        
        # Atribui o nome da rede se existir uma rede associada ao posto.
        nome_rede = rede_posto.nome if rede_posto else None
       
        # Se existir uma última cobrança, atribui os valores relevantes. Caso contrário, atribui None.
        if ultima_cobranca:
            valor_total_cobranca = ultima_cobranca.cobrado_total
            invoice_date = ultima_cobranca.invoice_date
        else:
            valor_total_cobranca = None
            invoice_date = None
        
        # Verifica a próxima atualização, baseada no tipo de cobrança e no status do produto.
        data_proxima_atualizacao, atualizar, id_typebillinng = checar_atualizacao(proxima_atualizacao, prod.status)
        
        # Adiciona um dicionário com os dados do produto à lista.
        produtos_list.append({
            'produto': prod,
            'posto': posto_relacionado,
            'valor_cobranca': valor_total_cobranca,
            'invoice_date': invoice_date,
            'idtypebiling': id_typebillinng,
            'atualizar': atualizar,
            'data_atualizacao': data_proxima_atualizacao,
            'nome_rede': nome_rede
        })

    # Renderiza a página HTML com a lista de produtos e seus respectivos dados.
    return render(request, 'core/historico_lista_produtos.html',
                  {'produtos_list': produtos_list})


# Essa função é responsável por buscar a lista de cobranças históricas de um produto específico.
def historico_lista_cobrancas(request, produto_id):
    # Busca o produto pelo seu ID. Utiliza o método select_related para efetuar uma "junção" 
    # com a tabela 'posto_id', melhorando a performance da consulta.
    prod = get_object_or_404(Produto.objects.select_related('posto_id'), pk=produto_id)
    
    # Filtra as cobranças associadas ao produto, ordenadas pela data da fatura.
    cobrancas = Billing.objects.filter(produto_id=prod).order_by('-invoice_date')
    
    # Busca o tipo de cobrança associado ao produto.
    tipo_cobranca = Type_billing.objects.filter(produto_id=prod).first()
    
    # Atribui o posto relacionado ao produto.
    posto_relacionado = prod.posto_id
    
    cobrancas_list = []
    
    # Percorre as cobranças do produto, atribuindo valores para exibição na lista.
    for cobranca in cobrancas:
        valor_total_cobranca = cobranca.cobrado_total
        invoice_date = cobranca.invoice_date
        
        cobrancas_list.append({
            'cobranca': cobranca,
            'valor_total': valor_total_cobranca,
            'invoice_date':  invoice_date,
        })

    # Renderiza a página HTML com o histórico de cobranças do produto.
    return render(request, 'core/historico_lista_cobrancas.html',
                  {'posto_relacionado': posto_relacionado,
                   'tipo_cobranca': tipo_cobranca,
                   'produto': prod,
                   'cobrancas_list': cobrancas_list})

## Detalhes da cobrança ####
# Essa função é responsável por retornar os detalhes de uma cobrança específica.
@require_GET
def cobranca_detalhes(request, billing_id):
    # Busca a cobrança pelo seu ID.
    cobranca = get_object_or_404(Billing, id=billing_id)
    # Renderiza a página HTML com os detalhes da cobrança.
    return render(request, 'core/cobranca_detalhes.html', {'cobranca': cobranca})

## Atualização de status da cobrança
# Essa função é responsável por atualizar o status de uma cobrança.
@require_http_methods(["GET", "POST"])
def edit_billing_status(request, billing_id):
    # Busca a cobrança pelo seu ID.
    cobranca = get_object_or_404(Billing, id=billing_id)
   
    if request.method == 'POST':
        # Se a requisição for um POST, cria um formulário com os dados enviados e a instância da cobrança.
        form = BillingStatusForm(request.POST, instance=cobranca)
        if form.is_valid():
            # Se o formulário for válido, salva as alterações e redireciona para a página de detalhes da cobrança.
            form.save()
            return redirect('cobranca_detalhes', billing_id=cobranca.id)
    else:
        # Se a requisição for um GET, cria um formulário com a instância da cobrança.
        form = BillingStatusForm(instance=cobranca)
    
    # Renderiza a página HTML para editar o status da cobrança.
    return render(request, 'core/edit_billing_status.html', 
                  {'form': form, 'Billing': cobranca})

# Atualização pela inflação
# Essa função é responsável por atualizar a inflação de um tipo de cobrança.
@require_http_methods(["GET", "POST"])
def atualizar_inflacao(request, type_billing_id):
    # Busca o tipo de cobrança pelo seu ID.
    item = get_object_or_404(Type_billing, id=type_billing_id)
    # Calcula o IPCA acumulado.
    ipca = ipca_acumulado()
    
    if request.method == 'POST':
        # Se a requisição for um POST, cria um formulário com os dados enviados e a instância do tipo de cobrança.
        form = Atualizacao(request.POST, instance=item)
        if form.is_valid():
            # Se o formulário for válido, salva as alterações e redireciona para a página de histórico de produtos.
            form.save()
            return redirect('historico_lista_produtos')
        else:
            # Se o formulário não for válido, retorna os erros do formulário como JSON.
            return JsonResponse(form.errors, status=400)
    else:
        # Se a requisição for um GET, cria um formulário com a instância do tipo de cobrança.
        form = Atualizacao(instance=item)

    # Renderiza a página HTML para atualizar a inflação.
    return render(request, 'core/atualizar_inflacao.html', 
                  {'form': form, 'ipca': ipca})
