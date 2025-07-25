import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from django.conf import settings

def send_email(subject, body, recipients=[], file_path=None):
    
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = settings.EMAIL
    sender_password = settings.EMAIL_PASSWORD

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = "Shopify Store <store@shopify.com>"
    msg['To'] = ', '.join(recipients)
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    if file_path:
        
        if os.path.exists(file_path):
            
            attachment = open(file_path, 'rb')
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')
            msg.attach(part)
            
        else:
            print("File not found, skipping attachment.")
        
    
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, recipients, text)
        