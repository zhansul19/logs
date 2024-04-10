import smtplib
from email.message import EmailMessage
from celery import Celery
import os
from dotenv import load_dotenv
from routes.notification import check_database_startup


load_dotenv()
SMTP_HOST = os.getenv("smtp_host")
SMTP_PORT = 25

celery = Celery('tasks', broker='redis://127.0.0.1:6379')
celery.conf.broker_connection_retry_on_startup = True


def get_email_template(message: str):
    email = EmailMessage()
    email['Subject'] = 'Risked searches'
    email['From'] = os.getenv("smtp_user")
    email['To'] = os.getenv("smtp_consumer")

    email.set_content(
        '<div>'
        f'<h3> {message}</h3>'
        '</div>',
        subtype='html'
    )
    return email


@celery.task
def send_email_report(username: str):
    email = get_email_template(username)
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.connect(SMTP_HOST, 587)
        server.starttls()
        server.login(os.getenv("smtp_user"), os.getenv("smtp_password"))
        server.send_message(email)
