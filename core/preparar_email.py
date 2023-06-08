import smtplib
from email.message import EmailMessage
from .email_data import EmailData
from .api_egestor import cobranca_boleto


def enviar_email_cobranca(dados_cobranca):
    
    email_data = EmailData(dados_cobranca)
    
    subject, email_body, billing_email = email_data.prepare_email()
    
    codPlanoContas, descricao, valor, dtVenc, dtCred, codContato, deretorio, nome_boleto, posto, cnpj, produto = email_data.dados_cobranca()
    
    pdf_path_boleto, pdf_path_recibo  = cobranca_boleto(codPlanoContas, descricao, valor, dtVenc, dtCred, codContato, deretorio, nome_boleto, posto, cnpj, produto)
    
    send_email_with_attachment(subject, email_body, billing_email, pdf_path_boleto, pdf_path_recibo)

def send_email_with_attachment(email_subject, corpo_email, destinatarios, pdf_path_boleto, pdf_path_recibo):
    
    # Configurações do e-mail
    # Precisa ver uma melhor forma de ocultar esses dados
    sender_email = "rtishower@rtisolutions.com.br"
    password = 'nemer2013*'
    
    # Cria o objeto de e-mail
    email_message = EmailMessage()
    email_message["From"] = sender_email
    email_message["Subject"] = email_subject
    email_message.set_content(corpo_email)
    
    # Adiciona os destinatários
    email_message["To"] = ", ".join(destinatarios)
    
    # Lê o arquivo PDF Boleto
    with open(pdf_path_boleto, 'rb') as attachment:
        # Adiciona o anexo ao e-mail
        email_message.add_attachment(attachment.read(), maintype='application', subtype='pdf', filename='Boleto.pdf')

    # Lê o arquivo PDF Recibo
    with open(pdf_path_recibo, 'rb') as attachment:
        # Adiciona o anexo ao e-mail
        email_message.add_attachment(attachment.read(), maintype='application', subtype='pdf', filename='Recibo.pdf')
    
    # Configuração do SMTP
    smtp_server = 'email-ssl.com.br'
    smtp_port = 465

    try:
        # Envia o e-mail
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, password)
            server.send_message(email_message)
        print("E-mail enviado com sucesso!")
    except Exception as e:
        print(f"Ocorreu um erro ao enviar o e-mail: {str(e)}")
