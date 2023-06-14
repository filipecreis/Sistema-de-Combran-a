"""""
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
"""""