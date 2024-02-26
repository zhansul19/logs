from fastapi import APIRouter, HTTPException, Depends
from logger import logging
from database import Log, User, get_db
from auth import get_current_user
from sqlalchemy.orm import Session
from sqlalchemy import String, cast

router = APIRouter()


@router.get("/log/{tag}={value}")
async def search_log_entries_by_request_body_value(tag: str, value: str, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    if tag == "username":
        log_entries = db.query(Log.username, User.email, Log.request_body, Log.request_rels, Log.date,Log.approvement_data, Log.obwii, Log.depth_, Log.limit_).join(User,Log.username == User.username).filter( Log.username == value).all()
        logging.info(f"{value}", extra={'user': current_user, 'table': 'itap',
                                        'action': 'поиск пользователя по username'})
    elif tag == "search":
        log_entries = db.query(Log.username, User.email, Log.request_body, Log.request_rels, Log.date,Log.approvement_data, Log.obwii, Log.depth_, Log.limit_).join(User,Log.username == User.username).filter( cast(Log.request_body, String).contains(value)).all()
        logging.info(f"{value}", extra={'user': current_user, 'table': 'itap',
                                        'action': 'поиск по иин'})
    elif tag == "fullname":
        log_entries = db.query(Log.username, User.email, Log.request_body, Log.request_rels, Log.date,Log.approvement_data, Log.obwii, Log.depth_, Log.limit_).join(User,Log.username == User.username).filter( cast(User.email, String).contains(value)).all()
        logging.info(f"{value}", extra={'user': current_user, 'table': 'itap',
                                        'action': 'поиск пользователя по фио'})
    log_entries_as_dict = [
        dict(
            username=row[0], email=row[1], request_body=row[2], request_rels=row[3],
            date=row[4], approvement_data=row[5], obwii=row[6], depth_=row[7], limit_=row[8]
        )
        for row in log_entries
    ]
    if not log_entries_as_dict:
        raise HTTPException(status_code=404, detail="User's log entries not found")
    return log_entries_as_dict