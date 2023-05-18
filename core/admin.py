from django.contrib import admin
from .models import (Posto, 
                     Produto, 
                     Tipo_produto, 
                     Billing, 
                     Type_billing, 
                     Ordem_servico, 
                     Rede_cliente)


admin.site.register(Posto)
admin.site.register(Produto)
admin.site.register(Tipo_produto)
admin.site.register(Billing)
admin.site.register(Ordem_servico)
admin.site.register(Type_billing)
admin.site.register(Rede_cliente)