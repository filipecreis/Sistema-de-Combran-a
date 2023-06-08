from django.conf.urls import url, include
from .views_historico import produtos_historico_cobranca, historico_lista_cobrancas, cobranca_detalhes, edit_billing_status, atualizar_inflacao
from .views_cobranca import (
    lista_cobranca,
    efetuar_cobranca,
    recalcular,
    valor_nota,
    prepara_email
    )

urlpatterns = [
    
    url(r'^lista_produtos_historico/$', produtos_historico_cobranca, name='historico_lista_produtos'),
    url(r'^lista_produtos_historico/lista_cobrancas/(?P<produto_id>\d+)/$', historico_lista_cobrancas, name='historico_lista_cobrancas'),
    url(r'^cobranca/(?P<billing_id>\d+)/$', cobranca_detalhes, name='cobranca_detalhes'),
    url(r'^edit_billing_status/(?P<billing_id>\d+)/$', edit_billing_status, name='edit_billing_status'),
    
    url(r'^atualizar_inflacao/(?P<type_billing_id>\d+)/$', atualizar_inflacao, name='atualizar_inflacao'),
    
    url(r'^cobranca/$', lista_cobranca, name='principal_cobranca'),
    url(r'^cobranca/efetuar_cobranca/(?P<produto_id>\d+)/$', efetuar_cobranca, name='efetuar_cobranca'),
    url(r'^valor_nota/(?P<produto_id>\d+)/$', valor_nota, name='valor_nota'),

    
   
    url(r'^cobranca/recalcular/$', recalcular, name='recalcular'),
    url(r'^cobranca/calcular/(?P<produto_id>\d+)/$', valor_nota, name='calcular'),
    
    url(r'^enviar_email/$', prepara_email, name='enviar_email'),
    
    
]


"""
    url(r'^$', home, name = 'core_home'),
    url(r'^listacliente/$', lista_clientes, name = 'lista_clientes'),
    url(r'^cadastrocliente/$', cadastro_cliente, name = 'cadastro_cliente'),
    url(r'^clientesalvo/$', cliente_salvo, name = 'cliente_salvo'),
    url(r'^clienteupdate/(?P<id>\d+)/$', cliente_update, name = 'cliente_update'),
    url(r'^clientedelete/(?P<id>\d+)/$', cliente_delete, name = 'cliente_delete'),
    
    
    url(r'^cadastroproduto/$', lista_cadastro_cliente, name='lista_cadastro_cliente'),
    url(r'^cadastroproduto/cliente/(?P<cliente_id>\d+)/$', cadastro_produto_cliente, name='cadastro_produto_cliente'),
    url(r'^cadastro_tipobilling/produto/(?P<produto_id>\d+)/$', cadastro_tipo_billing, name='cadastro_tipo_billing'),
    url(r'^atualizar_produto/(?P<produto_id>\d+)/$', atualizar_produto, name='atualizar_produto'),
    
    lista_clientes,
    cadastro_cliente,  
    cliente_salvo, 
    cliente_update, 
    cliente_delete,
    lista_cadastro_cliente,
    cadastro_produto_cliente,
    cadastro_tipo_billing,
    atualizar_produto,
    """
