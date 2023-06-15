from .models import  Billing
from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
import re


class EmailData:
    def __init__(self, billing_data):
        self.billing_data = billing_data
        self.product_data = billing_data.produto_id
        self.station_data = self.product_data.posto_id
        self.product_type = self.product_data.tipo_produto_id
        self.billing = Billing.objects.filter(produto_id=self.billing_data.produto_id).exclude(status=0).order_by('-id')[:2]
        self.current_billing = self.billing[0]
        self.previous_billing = self.billing[1] if len(self.billing) == 2 else 0

    def calculate_values(self):
        self.current_encerrante = self.current_billing.encerrante
        self.previous_encerrante = self.previous_billing.encerrante if self.previous_billing else 0
        self.encerrante_diff = self.current_encerrante - self.previous_encerrante

    def format_values(self, value):
        return "{:.2f}".format(value)

    def get_email_variables(self):
        self.calculate_values()
        email_variables = {
            "{posto}": self.station_data.nome, 
            "{nome_financeiro}": self.billing_data.nome_financeiro,
            "{mes_atual}": datetime.now().strftime("%m-%Y"), 
            "{mes_anterior}": (datetime.now() - relativedelta(months=1)).strftime("%m-%Y"),
            "{produto}": self.product_type.nome,
            "{moedeiro_v}": self.format_values(self.billing_data.moedeiro_encerrante),
            "{pago_v}": self.format_values(self.billing_data.pago),
            "{bonificado_v}": self.format_values(self.billing_data.bonificado), 
            "{gerencial_v}": self.format_values(self.billing_data.gerencial),
            "{gotas_v}": self.format_values(self.billing_data.pago_gotas),
            "{gotas_integrada_v}": self.format_values(self.billing_data.integracao_gotas),
            "{moedeiro_q}": str(self.encerrante_diff),
            "{pago_q}": str(self.current_billing.quant_pago),
            "{bonificado_q}": str(self.current_billing.quant_bonificado),
            "{gerencial_q}": str(self.current_billing.quant_gerencial),
            "{gotas_q}": str(self.current_billing.quant_pago_gotas),
            "{gotas_integrada_q}": str(self.current_billing.quant_integracao_gotas),
            "{moedeiro_t}": self.format_values(self.encerrante_diff * self.billing_data.moedeiro_encerrante),
            "{pago_t}": self.format_values(self.current_billing.quant_pago * self.billing_data.pago),
            "{bonificado_t}": self.format_values(self.current_billing.quant_bonificado * self.billing_data.bonificado),
            "{gerencial_t}": self.format_values(self.current_billing.quant_gerencial * self.billing_data.gerencial),
            "{gotas_t}": self.format_values(self.current_billing.quant_pago_gotas * self.billing_data.pago_gotas),
            "{gotas_integrada_t}": self.format_values(self.current_billing.quant_integracao_gotas * self.billing_data.integracao_gotas),
            "{fixo_variavel}": self.format_values(self.current_billing.fixo_variavel),
            "{fixo}": self.format_values(self.current_billing.fixo),
            "{vencimento_boleto}": self.current_billing.pay_date.strftime("%d/%m/%Y"),
            "{valor_boleto}": self.format_values(self.current_billing.cobrado_total),
            "{total_vaucher}": str(self.encerrante_diff + self.current_billing.quant_pago + self.current_billing.quant_bonificado + self.current_billing.quant_gerencial + self.current_billing.quant_pago_gotas+ self.current_billing.quant_integracao_gotas),
        }
        
        return email_variables

    def prepare_email(self):
        email_variables = self.get_email_variables()
        email_body = self.billing_data.corpo_email
        
        total = 0
        for key, value in email_variables.items():
            email_body = email_body.replace(key, value)
            if key.endswith("_t}"):
                total += float(value)
                
        
        if total > self.billing_data.maximo and self.billing_data.maximo != 0:
            email_body = email_body.replace("{msg_max_min}", f"Vale ressaltar que o valor calculado excedeu o valor máximo estabelecido em contrato de R$ {self.format_values( self.billing_data.minimo)}.")
        elif total < self.billing_data.minimo:
            email_body = email_body.replace("{msg_max_min}", f"Vale ressaltar que o valor calculado não excede o valor mínimo estabelecido em contrato de R$ {self.format_values(self.billing_data.minimo)}.")
        else:
            email_body = re.sub(r"\{msg_max_min\}[\n\r]*", "", email_body)

        if self.current_billing.desconto:
            email_body = email_body.replace("{desconto}", f"Desconto Concedido: R$ {self.format_values(self.current_billing.desconto)}")
        else:
            email_body = re.sub(r"{desconto}[\n\r].", "", email_body, flags=re.DOTALL)
        
        
        subject = f'Boleto ' + self.product_type.nome + ' - ' + self.station_data.nome + ' - RTI Soluctions'
        billing_email = self.billing_data.email_cobranca.split(';')
        
        return subject, email_body, billing_email
    
    def descricao_nome(self):
        
        if(self.billing_data.venda):
            return 'Comodato'
        else:
            return  'Locação'
    
    def dados_cobranca(self):
    
        # Nome recibo
        nome_posto = self.station_data.nome
        produto = self.product_type.nome
        cnpj = self.station_data.cnpj
        
        # Dados do boleto
        codPlanoContas = self.product_type.codigo_egestor# Int
        descricao =  f'{self.descricao_nome()} - {produto} - {nome_posto}'# String
        valor =  self.current_billing.cobrado_total # Float
        dtVenc = self.current_billing.pay_date.strftime("%Y-%m-%d") #String
        dtCred = (self.current_billing.pay_date + timedelta(days=1)).strftime("%Y-%m-%d")
        codContato = self.station_data.id_egestor
        
        # Diretôrio = estado / produto / posto
        estado = self.station_data.estado
        
        deretorio = f'{estado}/{produto}/{nome_posto}'
        nome_boleto = f'Boleto - {descricao}'
        
        return codPlanoContas, descricao, valor, dtVenc, dtCred, codContato, deretorio, nome_boleto, nome_posto, cnpj, produto
        