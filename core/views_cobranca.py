from django.shortcuts import render, redirect, get_object_or_404
from .models import Produto, Type_billing, Billing, Rede_cliente
from .forms import BillingStatusForm, Atualizacao, BillingVendaFixaForm
from datetime import datetime
from .auxiliar import total_cobrado, checar_atualizacao
from django.http import JsonResponse, HttpResponse
from django.urls import reverse


### cobranças

def lista_cobranca(request):
    
    produtos_ativos = Produto.objects.filter(status=True)
    produtos_list = []
    
    for prod in produtos_ativos:
        
        ultima_cobranca = Billing.objects.filter(produto_id=prod).order_by('-invoice_date').first()
        
        if ultima_cobranca:
            mes_ultima_cobranca = ultima_cobranca.invoice_date.month
            ano_ultima_cobranca = ultima_cobranca.invoice_date.year
        else:
            ultima_cobranca = None
            mes_ultima_cobranca = None
            ano_ultima_cobranca = None
            
        
        if mes_ultima_cobranca != datetime.now().month or ano_ultima_cobranca != datetime.now().year or ultima_cobranca == None  or ultima_cobranca.status == 0:
            
            posto_relacionado = prod.posto_id.nome
            proxima_atualizacao = Type_billing.objects.filter(produto_id=prod).first()
            rede_posto = prod.posto_id.rede_id
            
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

            ## Habilitar link de atualização
            data_proxima_atualizacao, atualizar, id_typebillinng = checar_atualizacao(proxima_atualizacao)
            
            produtos_list.append({
                'produto': prod,
                'posto': posto_relacionado,
                'valor_cobranca': valor_total_cobranca,
                'invoice_date': invoice_date,
                'idtypebiling': id_typebillinng,
                'atualizar': atualizar,
                'data_atualizacao':  data_proxima_atualizacao,
                'nome_rede': nome_rede
            })

    return render(request, 'cobranca/principal_cobranca.html', 
                  {'produtos_list': produtos_list})


def efetuar_cobranca(request, produto_id):
    
    dados_cobranca = Type_billing.objects.filter(produto_id=produto_id).first() 
    
    if dados_cobranca is None:
        return HttpResponse('Efetue o cadastro dos dados de cobrança', status=404)
    elif dados_cobranca.venda != 0:
        return cobranca_venda(request, produto_id, dados_cobranca)
    elif dados_cobranca.fixo != 0 and dados_cobranca.moedeiro_encerrante:
        return cobranca_fixa(request, produto_id)
    #elif dados_cobranca.moedeiro_encerrante != 0:
        #return cobranca_moedeiro(request, produto_id)
    #elif dados_cobranca.recorrente != 0:
        #return cobranca_recorrente(request, produto_id)
    else:
        return HttpResponse('Nenhum método de cobrança válido encontrado.', status=400)


def cobranca_venda(request, produto_id, dados_cobranca):
    
    if dados_cobranca.parcela_venda == 0:
        return comodato(request, produto_id) 
    else:
        return parcela_fixa(request, produto_id, dados_cobranca)


def parcela_fixa(request, produto_id, dados_cobranca):
    
    produto = Produto.objects.get(id=produto_id)
    divida_remanescente = dados_cobranca.venda - total_cobrado(produto_id)
    
    if divida_remanescente > dados_cobranca.parcela_venda:
        cobrar_parcela = dados_cobranca.parcela_venda

    else:
        cobrar_parcela = divida_remanescente

    if request.method == 'POST':
        form = BillingVendaFixaForm(request.POST)
        if form.is_valid():
            Billing = form.save(commit=False)  # cria o objeto sem salvar no banco ainda
            Billing.produto_id = produto  # vincula o produto ao objeto de cobrança
            Billing.status = 1
            Billing.save()  # agora sim, salva o objeto no banco
            return redirect('efetura cobrança')
    else:
        form = BillingVendaFixaForm(initial={
            'cobrado_total': cobrar_parcela,
            'produto_id': produto,
        })

    recalcular_url = reverse('recalcular')

    return render(request, 'cobranca/parcela_fixa.html', {
        'form': form,
        'recalcular_url': recalcular_url,
    })


def recalcular(request):
    if request.method == 'POST':
        form = BillingVendaFixaForm(request.POST)
        if form.is_valid():
            desconto = form.cleaned_data.get('desconto', 0)
            cobrado_total = form.cleaned_data.get('cobrado_total', 0)
            cobrado_total -= desconto
            return JsonResponse({'cobrado_total': cobrado_total})
        else:
            return JsonResponse({'error': 'Invalid form'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


def cobranca_fixa(request, produto_id):
    a =1


def cobranca_moedeiro(request, produto_id):
    a= 1


def cobranca_recorrente(request, produto_id):
    a = 1
  
  
def comodato(request, produto_id):
    
    dados_de_cobranca = Type_billing.objects.filter(produto_id=produto_id).first()
