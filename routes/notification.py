from fastapi import APIRouter, WebSocket, Depends, HTTPException
from sqlalchemy.orm import Session
from database import Log, Administration, get_db
import asyncio
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
import datetime

router = APIRouter()
# WebSocket connections
active_connections = set()
load_dotenv()


async def send_email(message: str):
    smtp_server = os.getenv("smtp_host")
    smtp_port = 25  # Default SMTP port

    try:
        # Establish connection to SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.connect(smtp_server, 587)
        server.starttls()  # Start TLS for secure connection
        server.login(os.getenv("smtp_user"), os.getenv("smtp_password"))  # Login to SMTP server

        # Create email message
        msg = MIMEText(message)
        msg['From'] = os.getenv("smtp_user")
        msg['To'] = os.getenv("smtp_consumer")
        msg['Subject'] = "Поиск рисковых логов"

        # Send email
        server.sendmail(os.getenv("smtp_user"), os.getenv("smtp_consumer"), msg.as_string())

        # Close connection to SMTP server
        server.quit()

        return {"message": "Email sent successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


async def check_database_for_changes_alchemy(websocket: WebSocket, db):
    last_review_id = 0
    while True:
        log_entries = (db.query(Log.username, Log.date, Log.id, Administration.iin, Administration.fio)
                       .join(Administration, Log.obwii.like('%' + Administration.iin + '%'))
                       .filter(Log.id > last_review_id)
                       .order_by(Log.date.desc()).all())
        if log_entries:
            for review in log_entries:
                formatted_date = review[1].strftime('%Y-%m-%d')  # Format the datetime object
                today_date = datetime.datetime.now().strftime('%Y-%m-%d')  # Get today's date
                if formatted_date == today_date:
                    data = {
                        "New search": f"('{review[0]}', {formatted_date}, {review[2]}, '{review[3]}', '{review[4]}')"
                    }
                    await websocket.send_json(data)
                    await send_email(review[0] + " искал " + review[4] + " в " + formatted_date)
                    # await websocket.send_text(review[0]+" искал "+review[4])
                    last_review_id = review[2]

        await asyncio.sleep(10)

async def check_database_for_changes_alchemy2(websocket: WebSocket, db):
    last_review_id = 0
    while True:
        log_entries = (db.query(Log.username, Log.date, Log.id, Administration.iin, Administration.fio)
                       .join(Administration, Log.obwii.like('%' + Administration.iin + '%'))
                       .filter(Log.id > last_review_id)
                       .order_by(Log.date.desc()).all())
        if log_entries:
            for review in log_entries:
                formatted_date = review[1].strftime('%Y-%m-%d')  # Format the datetime object
                today_date = datetime.datetime.now().strftime('%Y-%m-%d')  # Get today's date
                if formatted_date == today_date:
                    data = {
                        "New search": f"('{review[0]}', {formatted_date}, {review[2]}, '{review[3]}', '{review[4]}')"
                    }
                    await websocket.send_json(data)
                    await send_email(review[0] + " искал " + review[4] + " в " + formatted_date)
                    # await websocket.send_text(review[0]+" искал "+review[4])
                    last_review_id = review[2]

        await asyncio.sleep(10)
# WebSocket endpoint
# @router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket,
                             db: Session = Depends(get_db)):
    await websocket.accept()
    active_connections.add(websocket)
    try:
        while True:
            await websocket.send_json({"message": "Connected to WebSocket"})
            await check_database_for_changes_alchemy(websocket, db)
    finally:
        active_connections.remove(websocket)
