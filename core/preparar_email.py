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


from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def send_email_with_attachment(email_subject, corpo_email, destinatarios, pdf_path_boleto, pdf_path_recibo):
    # Configurações do e-mail
    sender_email = "rtishower@rtisolutions.com.br"
    password = 'nemer2013*'
    
    # Cria o objeto de e-mail
    email_message = MIMEMultipart("alternative")
    email_message["From"] = sender_email
    email_message["Subject"] = email_subject
    email_message["To"] = ", ".join(destinatarios)  # Adiciona os destinatários

    # Ler o arquivo HTML
    with open('core\\assinatura_email\\rtisolutions.com.br_assinatura_Recepcao.html', 'r') as f:
        html_content = f.read()
    
    # Transforma quebras de linha em <br> e espaços múltiplos são preservados
    corpo_email_html = f"<pre style='font-family: Arial, sans-serif;'>{corpo_email}</pre>"

    # Combina o corpo do e-mail e o HTML em uma parte
    html_part = MIMEText(f"{corpo_email_html}<br><br>{html_content}", "html")
    email_message.attach(html_part)
    
    # Lê o arquivo PDF Boleto e anexa ao e-mail
    with open(pdf_path_boleto, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename='Boleto.pdf')
        email_message.attach(part)
        
    # Lê o arquivo PDF Recibo e anexa ao e-mail
    with open(pdf_path_recibo, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename='Recibo.pdf')
        email_message.attach(part)
    
    # Configuração do SSL
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
