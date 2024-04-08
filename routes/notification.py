from fastapi import APIRouter, WebSocket, Depends, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import String, cast
from database import Log, Administration, get_db, get_db2
import asyncio
import datetime
from dotenv import load_dotenv
from tasks.tasks import send_email_report
import csv
from database import DossieLog
from sqlalchemy import or_, func


router = APIRouter()
# WebSocket connections
active_connections = set()
load_dotenv()


async def check_database_for_changes_alchemy(websocket: WebSocket, db):
    last_review_id = 0
    while True:
        log_entries = (db.query(Log.username, Log.date, Log.id, Administration.iin, Administration.fio)
                       .join(Administration, cast(Log.request_body, String).contains(Administration.iin))
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
                    try:
                        await websocket.send_json(data)  # Send notification to WebSocket clients
                    except WebSocketDisconnect:
                        # WebSocket client disconnected, handle it gracefully
                        pass
                    email_date = review[1].strftime('%Y-%m-%d %H:%M')
                    send_email_report.delay(f"{review[0]} искал {review[4]}-{review[3]} в {email_date}")
                    last_review_id = review[2]

        await asyncio.sleep(10)


async def check_database_for_changes_dossie_alchemy(websocket: WebSocket, db):
    last_review_id = 0
    while True:
        # Read the CSV file and extract ИИН values
        iin_values = []
        iin_to_fio_mapping = {}
        today_date = datetime.datetime.now().strftime('%Y-%m-%d')

        # with open('C:/Users/User6/Desktop/logs/log/administration2.csv', 'r', encoding='utf-8') as file:
        with open('/root/log_new/logs/administration2.csv', 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)
            for row in csv_reader:
                iin_values.append(row[3])
                iin_to_fio_mapping[row[3]] = row[2]

        # Constructing multiple like conditions
        like_conditions = [DossieLog.action.like(f'%{iin}%') for iin in iin_values]

        # Combining the like conditions using or_
        combined_condition = or_(*like_conditions)

        # Querying DossieLog entries
        log_entries = db.query(DossieLog).filter(func.DATE(DossieLog.log_time) == today_date).filter(DossieLog.id > last_review_id).filter(DossieLog.action.like('Поиск%')).filter(combined_condition).all()

        log_entries_as_dict = [
            dict(
                log_time=row.log_time, user_name=row.lname + " " + row.fname, iin=row.action, fio="", id=row.id
            )
            for row in log_entries
        ]

        for entry in log_entries_as_dict:
            for iin, fio in iin_to_fio_mapping.items():
                if iin in entry["iin"]:
                    entry["fio"] = fio
                    entry["iin"] = iin

        if log_entries_as_dict:
            for review in log_entries_as_dict:
                formatted_date = review['log_time'].strftime('%Y-%m-%d')  # Format the datetime object
                data = {
                    "New search": (review['user_name'], formatted_date, review['iin'], review['fio'])
                }
                try:
                    await websocket.send_json(data)  # Send notification to WebSocket clients
                except WebSocketDisconnect:
                    # WebSocket client disconnected, handle it gracefully
                    pass
                # email_date = review[1].strftime('%Y-%m-%d %H:%M')
                send_email_report.delay(f"{review['user_name']} искал {review['fio']}-{review['iin']} в {formatted_date}")
                last_review_id = review['id']

        await asyncio.sleep(10)


# WebSocket endpoint
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket,
                             db: Session = Depends(get_db),
                             db2: Session = Depends(get_db2)):
    await websocket.accept()
    active_connections.add(websocket)
    await websocket.send_json({"message": "Connected to WebSocket"})
    try:
        while True:
            await check_database_for_changes_alchemy(websocket, db)
            await check_database_for_changes_dossie_alchemy(websocket, db2)
    finally:
        active_connections.remove(websocket)
