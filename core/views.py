from django.shortcuts import render, redirect, get_object_or_404
from .models import Produto, Type_billing, Billing
from .forms import BillingStatusForm, Atualizacao
from datetime import datetime


def produtos_historico_cobranca(request):
    produtos = Produto.objects.all()
    produtos_list = []
    
    for prod in produtos:
        posto_relacionado = prod.posto_id.nome
        ultima_cobranca = Billing.objects.filter(produto_id=prod).order_by('-invoice_date').first()
        proxima_atualizacao = Type_billing.objects.filter(produto_id=prod).first()
    
        
        if ultima_cobranca:
            valor_total_cobranca = ultima_cobranca.cobrado_total
            invoice_date = ultima_cobranca.invoice_date
        else:
            valor_total_cobranca = None
            invoice_date = None
        
        
        if proxima_atualizacao:
            id_typebillinng = proxima_atualizacao.id
            data_proxima_atualizacao = proxima_atualizacao.data_atualizacao
        else:
            id_typebillinng = None
            data_proxima_atualizacao = None


        if proxima_atualizacao and proxima_atualizacao.data_atualizacao <= datetime.now().date():
            atualizar = True
            id_typebillinng = proxima_atualizacao.id
        
        else:
            atualizar = False
            id_typebillinng = None
        
        
        produtos_list.append({
            'produto': prod,
            'posto': posto_relacionado,
            'valor_cobranca': valor_total_cobranca,
            'invoice_date': invoice_date,
            'idtypebiling': id_typebillinng,
            'atualizar': atualizar,
            'data_atualizacao':  data_proxima_atualizacao,
        })

    return render(request, 'core/historico_lista_produtos.html', {'produtos_list': produtos_list})


def historico_lista_cobrancas(request, produto_id):
    prod = get_object_or_404(Produto, pk=produto_id)
    cobrancas = Billing.objects.filter(produto_id=prod).order_by('-invoice_date')
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

    return render(request, 'core/historico_lista_cobrancas.html', {'produto': prod, 'cobrancas_list': cobrancas_list})

## detalha a cobrança ####

def cobranca_detalhes(request, billing_id):
    cobranca = get_object_or_404(Billing, id=billing_id)
    return render(request, 'core/cobranca_detalhes.html', {'cobranca': cobranca})


def edit_billing_status(request, billing_id):
    cobranca = get_object_or_404(Billing, id=billing_id)
   
    if request.method == 'POST':
        form = BillingStatusForm(request.POST, instance=cobranca)
        if form.is_valid():
            form.save()
            return redirect('cobranca_detalhes', billing_id=cobranca.id)
    else:
        form = BillingStatusForm(instance=cobranca)
    
    return render(request, 'core/edit_billing_status.html', {'form': form, 'Billing': cobranca})


def atualizar_inflacao(request, type_billing_id):
    item = get_object_or_404(Type_billing, id=type_billing_id)

    if request.method == 'POST':
        form = Atualizacao(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('historico_lista_produtos')
        else:
            print(form.errors)  # Mostra os erros de validação
    else:
        form = Atualizacao(instance=item)

    return render(request, 'core/atualizar_inflacao.html', {'form': form})


"""
### Lista do cliente   #####

def lista_clientes(request):
    query = request.GET.get('q')
    if query:
        listapostos = posto.objects.filter(Q(nome__icontains=query) | Q(razao_social__icontains=query) | Q(cnpj__icontains=query))
    else:
        listapostos = posto.objects.all()

    form = PostoForm()
    data = {'listapostos': listapostos, 'form': form, 'query': query}
    return render(request, 'core/lista_cliente.html', data)


######## cadastro do cliente formulario  #####

def cadastro_cliente(request):
    listapostos = posto.objects.all()
    form = PostoForm()
    data = {'listapostos': listapostos, 'form': form}
    return render(request, 'core/cadastro_cliente.html', data)

##### Salvando os dados do formulario do cadastro #######

def cliente_salvo(request):
    form = PostoForm(request.POST or None)
    if form.is_valid():
        form.save()
    return redirect('cadastro_cliente')


##### pagina que atualiza os dados do cliente #######

def cliente_update(request, id):
    data = {}
    posto_instance = posto.objects.get(id=id)
    form = PostoForm(request.POST or None, instance=posto_instance)
    data['posto_instance'] = posto_instance
    data['form'] = form

    if request.method == 'POST':
        if form.is_valid():
            form.save()
        return redirect('cadastro_cliente')
    else:
        return render(request, 'core/cliente_update.html', data)


#### abre página para deletar os dados do cliente #####

def cliente_delete(request, id):

    posto_instance = posto.objects.get(id=id)

    if request.method == 'POST':
        posto_instance.delete()
        return redirect('cadastro_cliente')

    else:
        return render(request, 'core/deletar_cliente_confirma.html', {'posto_instance': posto_instance})


def cadastro_produto(request):

    query = request.GET.get('q')
    if query:
        listapostos = posto.objects.filter(Q(nome__icontains=query) | Q(razao_social__icontains=query) | Q(cnpj__icontains=query))
    else:
        listapostos = posto.objects.all()

    form = PostoForm()
    data = {'listapostos': listapostos, 'form': form, 'query': query}
    return render(request, 'core/lista_cadastro_produto.html', {'listapostos':  listapostos})

##### página do cadastro do produto ######

def lista_cadastro_cliente(request):
    query = request.GET.get('q')
    if query:
        listapostos = posto.objects.filter(Q(nome__icontains=query) | Q(razao_social__icontains=query) | Q(cnpj__icontains=query))
    else:
        listapostos = posto.objects.all()

    context = {
        'listapostos': listapostos,
        'query': query
    }

    return render(request, 'core/lista_cadastro_produto.html', {'listapostos':  listapostos})


def cadastro_produto_cliente(request, cliente_id):
    cliente = get_object_or_404(posto, id=cliente_id)
    form_produto = ProdutoForm(request.POST or None)

    if request.method == "POST":
        if form_produto.is_valid():
            novo_produto = form_produto.save(commit=False)
            novo_produto.posto = cliente
            novo_produto.save()

            return redirect('cadastro_tipo_billing', produto_id=novo_produto.id)

    posto_id = cliente_id
    posto_obj = posto.objects.get(id=posto_id)
    produtos_vinculados = produto.objects.filter(posto=posto_obj)

    context = {
        'form_produto': form_produto,
        'cliente': cliente,
        'produtos_vinculados': produtos_vinculados
    }

    return render(request, 'core/cadastro_produto_cliente.html', context)


def cadastro_tipo_billing(request, produto_id):
    produto_obj = get_object_or_404(produto, id=produto_id)
    form_tipo_produto = TipoProdutoForm(request.POST or None, instance=tipo_produto(produto=produto_obj))
    form_tye_billing = TyeBillingForm(request.POST or None, instance=Type_billing
(produto=produto_obj))

    if request.method == "POST":
        if form_tipo_produto.is_valid() and form_tye_billing.is_valid():
            tipo_produto_obj = form_tipo_produto.save()
            tye_billing_obj = form_tye_billing.save()

            return redirect('cadastro_produto_cliente', cliente_id=produto_obj.posto.id)

    context = {
        'form_tipo_produto': form_tipo_produto,
        'form_tye_billing': form_tye_billing,
        'produto': produto_obj
    }

    return render(request, 'core/cadastro_tipo_billing.html', context)


def atualizar_produto(request, produto_id):
    produto_obj = get_object_or_404(produto, id=produto_id)
    tipo_billing_obj = get_object_or_404(Type_billing
, produto=produto_obj)

    if request.method == "POST":
        form_produto = ProdutoForm(request.POST, instance=produto_obj)
        form_tipo_billing = TyeBillingForm(request.POST, instance=tipo_billing_obj)

        if form_produto.is_valid() and form_tipo_billing.is_valid():
            form_produto.save()
            form_tipo_billing.save()
            return redirect('lista_produtos') # Redirecionar para a página de lista de produtos

    else:
        form_produto = ProdutoForm(instance=produto_obj)
        form_tipo_billing = TyeBillingForm(instance=tipo_billing_obj)

    context = {
        'form_produto': form_produto,
        'form_tipo_billing': form_tipo_billing,
        'produto': produto_obj,
        'tipo_billing': tipo_billing_obj,
    }

    return render(request, 'core/atualizar_produto.html', context)

"""