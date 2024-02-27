from fastapi import APIRouter, HTTPException, Depends
from logger import logging
from database import UsersLog, Cascade, get_db
from auth import get_current_user
from sqlalchemy.orm import Session
from sqlalchemy import String, cast

router = APIRouter()

@router.get("/users_log/{tag}={value}")
async def get_users_log_entries_by_username(tag: str, value: str, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    if tag == "username":
        log_entries = (db.query(UsersLog.username,Cascade.name,UsersLog.message,UsersLog.debug_level,UsersLog.time)
                       .join(Cascade,UsersLog.username == Cascade.email)
                       .filter(UsersLog.username==value).order_by(UsersLog.time.desc()).all())
        logging.info(f"{value}",extra={'user': current_user, 'table': 'users_log_cascade', 'action': 'поиск пользователя по username'})
    elif tag == "fullname":
        log_entries = (db.query(UsersLog.username,Cascade.name,UsersLog.message,UsersLog.debug_level,UsersLog.time)
                       .join(Cascade,UsersLog.username == Cascade.email)
                       .filter(cast(Cascade.name, String).order_by(UsersLog.time.desc())
                               .contains(value)).all())
        logging.info(f"{value}", extra={'user': current_user, 'table': 'users_log_cascade', 'action': 'поиск пользователя по фио'})
    elif tag == "message":
        log_entries = (db.query(UsersLog.username,Cascade.name,UsersLog.message,UsersLog.debug_level,UsersLog.time)
                       .join(Cascade,UsersLog.username == Cascade.email)
                       .filter(cast(UsersLog.message, String).order_by(UsersLog.time.desc())
                               .contains(value)).all())
        logging.info(f"{value}",extra={'user': current_user, 'table': 'users_log_cascade', 'action': 'поиск по иин'})

    log_entries_as_dict = [
        dict(
            username=row[0], name=row[1], message=row[2], debug_level=row[3], time=row[4]
        )
        for row in log_entries
    ]
    if not log_entries_as_dict:
        raise HTTPException(status_code=404, detail="User's log entries not found")
    return log_entries_as_dict