from django.shortcuts import render, redirect, get_object_or_404
from .models import Produto, Type_billing, Billing
from .forms import BillingStatusForm, Atualizacao
from .auxiliar import checar_atualizacao, ipca_acumulado
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from django.http import JsonResponse

def produtos_historico_cobranca(request):
    
    # Inicializando a lista de produtos
    produtos_list = []
    
    # Obtendo o valor da pesquisa
    search_query = request.GET.get('search', '')

    # Consultando os produtos de acordo com a pesquisa
    if search_query:
        produtos = Produto.objects.filter(posto_id__nome__icontains=search_query)
    else:
        produtos = Produto.objects.all()
    
    # Ordenando os produtos e trazendo as relações com Billing e Type_billing
    produtos = produtos.order_by('-status').prefetch_related('billing_set', 'type_billing')

    for prod in produtos:
        posto_relacionado = prod.posto_id.nome
        rede_posto = prod.posto_id.rede_id
        ultima_cobranca = prod.billing_set.order_by('-invoice_date').first()
        proxima_atualizacao = prod.type_billing
        
        nome_rede = rede_posto.nome if rede_posto else None
       
        if ultima_cobranca:
            valor_total_cobranca = ultima_cobranca.cobrado_total
            invoice_date = ultima_cobranca.invoice_date
        else:
            valor_total_cobranca = None
            invoice_date = None
        
        data_proxima_atualizacao, atualizar, id_typebillinng = checar_atualizacao(proxima_atualizacao, prod.status)
        
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

    return render(request, 'core/historico_lista_produtos.html',
                  {'produtos_list': produtos_list})


def historico_lista_cobrancas(request, produto_id):
    prod = get_object_or_404(Produto.objects.select_related('posto_id'), pk=produto_id)
    cobrancas = Billing.objects.filter(produto_id=prod).order_by('-invoice_date')
    tipo_cobranca = Type_billing.objects.filter(produto_id=prod).first()
    posto_relacionado = prod.posto_id
    
    cobrancas_list = []
    
    for cobranca in cobrancas:
        valor_total_cobranca = cobranca.cobrado_total
        invoice_date = cobranca.invoice_date
        
        cobrancas_list.append({
            'cobranca': cobranca,
            'valor_total': valor_total_cobranca,
            'invoice_date':  invoice_date,
        })

    return render(request, 'core/historico_lista_cobrancas.html',
                  {'posto_relacionado': posto_relacionado,
                   'tipo_cobranca': tipo_cobranca ,
                   'produto': prod,
                   'cobrancas_list': cobrancas_list})

## detalha a cobrança ####
@require_GET
def cobranca_detalhes(request, billing_id):
    cobranca = get_object_or_404(Billing, id=billing_id)
    return render(request, 'core/cobranca_detalhes.html', {'cobranca': cobranca})

## atualizar pela inflação
@require_http_methods(["GET", "POST"])
def edit_billing_status(request, billing_id):
    cobranca = get_object_or_404(Billing, id=billing_id)
   
    if request.method == 'POST':
        form = BillingStatusForm(request.POST, instance=cobranca)
        if form.is_valid():
            form.save()
            return redirect('cobranca_detalhes', billing_id=cobranca.id)
    else:
        form = BillingStatusForm(instance=cobranca)
    
    return render(request, 'core/edit_billing_status.html', 
                  {'form': form, 'Billing': cobranca})


@require_http_methods(["GET", "POST"])
def atualizar_inflacao(request, type_billing_id):
    item = get_object_or_404(Type_billing, id=type_billing_id)
    ipca = ipca_acumulado()
    
    if request.method == 'POST':
        form = Atualizacao(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('historico_lista_produtos')
        else:
            # Return the form errors as JSON
            return JsonResponse(form.errors, status=400)
    else:
        form = Atualizacao(instance=item)

    return render(request, 'core/atualizar_inflacao.html', 
                  {'form': form, 'ipca': ipca})
    