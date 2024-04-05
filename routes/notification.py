from fastapi import APIRouter, WebSocket, Depends, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import String, cast
from database import Log, Administration, get_db
import asyncio
import datetime
from dotenv import load_dotenv
from tasks.tasks import send_email_report

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
                    send_email_report.delay(f"{review[0]} искал {review[0]} в {email_date}")
                    last_review_id = review[2]

        await asyncio.sleep(10)


# WebSocket endpoint
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket,
                             db: Session = Depends(get_db)):
    await websocket.accept()
    active_connections.add(websocket)
    await websocket.send_json({"message": "Connected to WebSocket"})
    try:
        while True:
            await check_database_for_changes_alchemy(websocket, db)
    finally:
        active_connections.remove(websocket)
