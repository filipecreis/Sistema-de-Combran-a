from django.shortcuts import render
from .models import Produto, Type_billing, Billing
from .forms import BillingForm, EmailForm
from datetime import datetime
from .auxiliar import total_cobrado, checar_atualizacao
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from .preparar_email import send_email_with_attachment,enviar_email_cobranca
from .email_data import EmailData
from .api_egestor import cobranca_boleto


def lista_cobranca(request):
    
    produtos_ativos = Produto.objects.filter(status=True)
    produtos_list = []
    
    for prod in produtos_ativos:
        
        ultima_cobranca = Billing.objects.filter(produto_id=prod).order_by('id').first()
        
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
            return prepara_email(request, produto_id,dados_cobranca)
    
    form = BillingForm(initial={'cobrado_total': float(cobrado_total)})
    
    return render(request, 'cobranca/calcularcobranca.html', {
         
        'on_precobranca_encerrante': on_precobranca_encerrante,
        'on_pago':on_pago,
        'on_bonificado':on_bonificado,
        'on_gerencial':on_gerencial,
        'on_pago_gotas':on_pago_gotas,
        'on_integracao_gotas':on_integracao_gotas,
        'recalcular_url': recalcular_url,
        'form': form
        
    })


def tipo_cobranca(dados_cobranca, produto_id):

    if dados_cobranca.parcela_venda != 0 or dados_cobranca.fixo:
       
        recalcular_url = reverse('recalcular')
        if dados_cobranca.parcela_venda != 0:
            divida_remanescente = dados_cobranca.venda - total_cobrado(produto_id)
            if divida_remanescente > dados_cobranca.parcela_venda:
                cobrado_total = dados_cobranca.parcela_venda

            else:
                cobrado_total = divida_remanescente
                
        else:
            cobrado_total = dados_cobranca.fixo
    
    else:
        cobrado_total = 0
        recalcular_url = reverse('valor_nota', args=[produto_id])
    
    return (recalcular_url, cobrado_total)


def recalcular(request):
    if request.method == 'POST':
        form = BillingForm(request.POST)
        if form.is_valid():
            
            desconto = form.cleaned_data.get('desconto', 0)
            cobrado_total = form.cleaned_data.get('cobrado_total', 0)
            cobrado_total -= desconto
            return JsonResponse({'cobrado_total': cobrado_total})
        else:
            print(form.errors)
            return JsonResponse({'error': 'Invalid form'}, status=400)
    
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


def valor_nota(request, produto_id):
    
    dados_cobranca = Type_billing.objects.filter(produto_id=produto_id).first()
    
    if request.method == 'POST':
        form = BillingForm(request.POST)
        if form.is_valid():
            
            encerrante = form.cleaned_data.get('encerrante', 0)
            pago = form.cleaned_data.get('quant_pago', 0)
            bonificado = form.cleaned_data.get('quant_bonificado', 0)
            gerencial = form.cleaned_data.get('quant_gerencial', 0)
            pago_gotas = form.cleaned_data.get('quant_pago_gotas', 0)
            integracao_gotas = form.cleaned_data.get('quant_integracao_gotas', 0)
            desconto = form.cleaned_data.get('desconto', 0)
            cobrado_total = formula_cobranca(desconto, encerrante, pago, bonificado, gerencial, pago_gotas, integracao_gotas, dados_cobranca)
            
            return JsonResponse({'cobrado_total': cobrado_total})
        else:
            return JsonResponse({'error': 'Invalid form'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


def formula_cobranca(desconto, encerrante, pago, bonificado, gerencial, pago_gotas, integracao_gotas, dados_cobranca):
    
    
    ultimo_encerrante = 0
    if(dados_cobranca.moedeiro_encerrante != 0):
        ultima_cobranca = Billing.objects.filter(produto_id=dados_cobranca.produto_id).exclude(status=0).order_by('id').first()
        
        if ultima_cobranca is not None:
            ultimo_encerrante = ultima_cobranca.encerrante
            
    total_encerrante = dados_cobranca.moedeiro_encerrante*(encerrante - ultimo_encerrante)
    total_pago = dados_cobranca.pago*pago
    total_bonificado = dados_cobranca.bonificado*bonificado
    total_gerencial = dados_cobranca.gerencial*gerencial
    total_pago_gotas = dados_cobranca.pago_gotas*pago_gotas
    total_integracao_gotas = dados_cobranca.integracao_gotas*integracao_gotas
    
    total = dados_cobranca.fixo_variavel + total_encerrante + total_pago + total_bonificado + total_gerencial + total_pago_gotas + total_integracao_gotas - desconto
    total = round(total, 2)
    
    if(total > dados_cobranca.maximo and dados_cobranca.maximo!=0):
        total = dados_cobranca.maximo
    elif(total < dados_cobranca.minimo):
        total = dados_cobranca.minimo
    
    return (total)


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


def prepara_email(request, produto_id, dados_cobranca):
    
    #email_data = EmailData(dados_cobranca)
    #subject, email_body, billing_email = email_data.prepare_email()
    #pdf_path_boleto, pdf_path_recibo  = cobranca_boleto()
    #send_email_with_attachment(subject, email_body, billing_email, pdf_path_boleto, pdf_path_recibo)
    enviar_email_cobranca(dados_cobranca)
    
    form = EmailForm()
    
    return render(request, 'cobranca/teste.html', {'form': form})
