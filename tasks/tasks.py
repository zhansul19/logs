import smtplib
from email.message import EmailMessage
from celery import Celery
import os
from dotenv import load_dotenv

from database import Log, Administration, get_db
from sqlalchemy import func
import datetime
from sqlalchemy import String, cast
import asyncio

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


def send_email_report(username: str):
    email = get_email_template(username)
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.connect(SMTP_HOST, 587)
        server.starttls()
        server.login(os.getenv("smtp_user"), os.getenv("smtp_password"))
        server.send_message(email)


@celery.task
async def check_database_startup():
    db = get_db()
    last_review_id = 0
    today_date = datetime.datetime.now().strftime('%Y-%m-%d')
    already_notified_reviews = set()
    while True:
        log_entries = (db.query(Log.username, Log.date, Log.id, Administration.iin, Administration.fio)
                       .join(Administration, cast(Log.request_body, String).contains(Administration.iin))
                       .filter(func.DATE(Log.date) == today_date)
                       .filter(Log.id > last_review_id)
                       .order_by(Log.date.desc()).all())
        if log_entries:
            for review in log_entries:
                if review[2] not in already_notified_reviews:
                    email_date = review[1].strftime('%Y-%m-%d %H:%M')
                    send_email_report.delay(f"{review[0]} искал {review[4]}-{review[3]} в {email_date}")
                    last_review_id = review[2]
                    already_notified_reviews.add(review[2])
        await asyncio.sleep(10)
