from .models import Type_billing, Billing
from .forms import BillingForm
from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Sum


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
        ultima_cobranca = Billing.objects.filter(produto_id=dados_cobranca.produto_id).exclude(status=0).order_by('-id').first()
        
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
    print(total)
    return (total)


def total_cobrado(produto_id):
    
    try:
        total_cobrado = Billing.objects.filter(produto_id=produto_id).exclude(status=0).aggregate(total=Sum('cobrado_total'))['total']
        return total_cobrado if total_cobrado else 0
    except Exception as e:
        print("Erro: ", e)
        return 0
