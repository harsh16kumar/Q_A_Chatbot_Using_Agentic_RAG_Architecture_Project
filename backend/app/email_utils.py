import smtplib
from email.mime.text import MIMEText
from app import config

def send_email(recipient, subject, body):
    # For now print; enable SMTP when credentials and security required
    if not config.SENDER_EMAIL or not config.APP_PASSWORD:
        print(f"[Email mock] To: {recipient} | Subject: {subject}\n{body}")
        return
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = config.SENDER_EMAIL
    msg["To"] = recipient
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(config.SENDER_EMAIL, config.APP_PASSWORD)
        server.send_message(msg)
    print("Email sent.")
