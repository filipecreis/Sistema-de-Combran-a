from django.shortcuts import render
from .models import Produto, Type_billing, Billing
from .forms import BillingForm
from django.shortcuts import redirect
from datetime import datetime
from django.http import HttpResponse
from .logica_cobranca import tipo_cobranca
from .preparar_email import enviar_email_cobranca
from .auxiliar import checar_atualizacao
from .teste import baixar_banco_dados_posto


def lista_cobranca(request):
    baixar_banco_dados_posto()
    produtos_ativos = Produto.objects.filter(status=True)
    produtos_list = []
    
    for prod in produtos_ativos:
        
        ultima_cobranca = Billing.objects.exclude(status=0).filter(produto_id=prod).order_by('id').last()
        
        
        if ultima_cobranca:
            mes_ultima_cobranca = ultima_cobranca.invoice_date.month
            ano_ultima_cobranca = ultima_cobranca.invoice_date.year
        else:
            ultima_cobranca = None
            mes_ultima_cobranca = None
            ano_ultima_cobranca = None
            
        if (mes_ultima_cobranca != datetime.now().month or ano_ultima_cobranca != datetime.now().year or ultima_cobranca == None) and  prod.data_instalacao.month < datetime.now().month:
            
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
            data_proxima_atualizacao, atualizar, id_typebillinng = checar_atualizacao(proxima_atualizacao, True)
            
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
    else:
        return inserir_dados_cobranca(request, produto_id, dados_cobranca)


def inserir_dados_cobranca(request, produto_id, dados_cobranca):
    
    on_precobranca_encerrante, on_pago, on_bonificado, on_gerencial, on_pago_gotas, on_integracao_gotas = habilitar(dados_cobranca)
    produto = Produto.objects.get(id=produto_id)
    
    recalcular_url, cobrado_total = tipo_cobranca(dados_cobranca, produto_id)
    
    if request.method == 'POST':
        form = BillingForm(request.POST)
        if form.is_valid():
            Billing = form.save(commit=False)
            Billing.produto_id = produto
            Billing.status = 1 # coloca a espera do pagamento
            Billing.save()
            
            enviar_email_cobranca(dados_cobranca)
            return redirect('principal_cobranca')
           
    form = BillingForm(initial={'cobrado_total': float(cobrado_total)})
    
    return render(request, 'cobranca/calcularcobranca.html', {
        'telefone': dados_cobranca.telefone_cobranca,
        'contrato': dados_cobranca.contrato,
        'produto': dados_cobranca.produto_id.nome,
        'posto': dados_cobranca.produto_id.posto_id.nome,
        'on_precobranca_encerrante': on_precobranca_encerrante,
        'on_pago':on_pago,
        'on_bonificado':on_bonificado,
        'on_gerencial':on_gerencial,
        'on_pago_gotas':on_pago_gotas,
        'on_integracao_gotas':on_integracao_gotas,
        'recalcular_url': recalcular_url,
        'form': form
    })


def habilitar(dados_cobranca):
    
    on_precobranca_encerrante = bool(dados_cobranca.moedeiro_encerrante)
    on_pago = bool(dados_cobranca.pago)
    on_bonificado = bool(dados_cobranca.bonificado)
    on_gerencial = bool(dados_cobranca.gerencial)
    on_pago_gotas = bool(dados_cobranca.pago_gotas)
    on_integracao_gotas = bool(dados_cobranca.integracao_gotas)

    return (on_precobranca_encerrante,
            on_pago,
            on_bonificado,
            on_gerencial,
            on_pago_gotas,
            on_integracao_gotas)
