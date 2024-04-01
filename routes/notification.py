from fastapi import APIRouter, WebSocket, Depends, HTTPException
from sqlalchemy.orm import Session
from database import Log, Administration, get_db
import asyncio

router = APIRouter()
# WebSocket connections
active_connections = set()


async def check_database_for_changes_alchemy(websocket: WebSocket, db):
    last_review_id = 0
    while True:
        log_entries = (db.query(Log.username, Log.date, Log.id, Administration.iin, Administration.fio)
                       .join(Administration, Log.obwii.like('%' + Administration.iin + '%'))
                       .filter(Log.id > last_review_id).all())
        if log_entries:
            for review in log_entries:
                formatted_date = review[1].strftime('%Y-%m-%d')  # Format the datetime object
                data = {
                    "New search": f"('{review[0]}', {formatted_date}, {review[2]}, '{review[3]}', '{review[4]}')"
                }
                await websocket.send_json(data)
                # await websocket.send_text(review[0]+" искал "+review[4])
                last_review_id = review[2]

        await asyncio.sleep(10)


# WebSocket endpoint
@router.websocket("/ws")
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
