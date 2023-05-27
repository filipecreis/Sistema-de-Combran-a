from django.shortcuts import render, redirect, get_object_or_404
from .models import Produto, Type_billing, Billing
from .forms import BillingStatusForm, Atualizacao
from .auxiliar import checar_atualizacao, ipca_acumulado

def produtos_historico_cobranca(request):
    
    produtos = Produto.objects.all().order_by('-status')
    produtos_list = []
    
    search_query = request.GET.get('search', '')
    if search_query:
        produtos = Produto.objects.filter(posto_id__nome__icontains=search_query).order_by('-status')
    else:
        produtos = Produto.objects.all().order_by('-status')
    
    
    for prod in produtos:
        posto_relacionado = prod.posto_id.nome
        rede_posto = prod.posto_id.rede_id
        ultima_cobranca = Billing.objects.filter(produto_id=prod).order_by('-invoice_date').first()
        proxima_atualizacao = Type_billing.objects.filter(produto_id=prod).first()
        
        if rede_posto:
            nome_rede = rede_posto.nome
        else:
            nome_rede = None
       
        if ultima_cobranca:
            valor_total_cobranca = ultima_cobranca.cobrado_total
            invoice_date = ultima_cobranca.invoice_date
        else:
            valor_total_cobranca = None
            invoice_date = None
        
        data_proxima_atualizacao, atualizar, id_typebillinng = checar_atualizacao(proxima_atualizacao)
        
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
    prod = get_object_or_404(Produto, pk=produto_id)
    cobrancas = Billing.objects.filter(produto_id=prod).order_by('-invoice_date')
    tipo_cobranca = Type_billing.objects.filter(produto_id=prod).first()
    posto_relacionado = prod.posto_id
    produto = prod
    
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
                   'produto': produto,
                   'cobrancas_list': cobrancas_list})

## detalha a cobrança ####

def cobranca_detalhes(request, billing_id):
    cobranca = get_object_or_404(Billing, id=billing_id)
    return render(request, 'core/cobranca_detalhes.html',
                  {'cobranca': cobranca})

## atualizar pela inflação

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
                  {'form': form,
                   'Billing': cobranca})


def atualizar_inflacao(request, type_billing_id):
    item = get_object_or_404(Type_billing, id=type_billing_id)
    ipca = ipca_acumulado()
    
    if request.method == 'POST':
        form = Atualizacao(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('historico_lista_produtos')
        else:
            print(form.errors)  # Mostra os erros de validação
    else:
        form = Atualizacao(instance=item)

    return render(request, 'core/atualizar_inflacao.html', 
                  {'form': form,
                   'ipca': ipca})
