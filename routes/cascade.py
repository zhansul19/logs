from fastapi import APIRouter, HTTPException, Depends, Query
from logger import logging
from database import UsersLog, Cascade, get_db
from auth import get_current_user
from sqlalchemy.orm import Session
from sqlalchemy import String, cast
import re

router = APIRouter()


@router.get("/users_log/{tag}={value}/")
async def get_users_log_entries_by_username(tag: str,
                                            value: str,
                                            start_date: str = Query(None),
                                            end_date: str = Query(None),
                                            current_user: str = Depends(get_current_user),
                                            db: Session = Depends(get_db)):
    log_entries = (db.query(UsersLog.username, Cascade.name, UsersLog.message, UsersLog.debug_level, UsersLog.time)
                   .join(Cascade, UsersLog.username == Cascade.email))
    if tag == "username":
        log_entries = log_entries.filter(UsersLog.username == value)
        logging.info(f"{value}", extra={'user': current_user, 'table': 'users_log_cascade', 'action': 'поиск пользователя по username'})
    elif tag == "username_partial":
        log_entries = log_entries.filter(cast(UsersLog.username, String).contains(value))
        logging.info(f"{value}", extra={'user': current_user, 'table': 'users_log_cascade', 'action': 'поиск пользователя по username'})
    elif tag == "fullname":
        log_entries = log_entries.filter(cast(Cascade.name, String).contains(value))
        logging.info(f"{value}", extra={'user': current_user, 'table': 'users_log_cascade', 'action': 'поиск пользователя по имени'})
    elif tag == "fullname_full":
        all_log_entries = (db.query(UsersLog.username, Cascade.name, UsersLog.message, UsersLog.debug_level, UsersLog.time)
                       .join(Cascade, UsersLog.username == Cascade.email)
                       .order_by(UsersLog.time.desc()).all())
        log_entries = []
        for log_entry in all_log_entries:
            name = log_entry.name
            if not value or re.search(r'\b{}\b'.format(re.escape(value)), name):
                log_entries.append(log_entry)
        logging.info(f"{value}", extra={'user': current_user, 'table': 'users_log_cascade', 'action': 'поиск пользователя по полному имени'})
    elif tag == "message":
        log_entries = log_entries.filter(cast(UsersLog.message, String).contains(value))
        logging.info(f"{value}", extra={'user': current_user, 'table': 'users_log_cascade', 'action': 'поиск по иин'})

    # Filter by date range
    if start_date:
        log_entries = log_entries.filter(cast(UsersLog.time, String) >= start_date)
    if end_date:
        log_entries = log_entries.filter(cast(UsersLog.time, String) <= end_date)

    log_entries = log_entries.order_by(UsersLog.time.desc()).all()

    log_entries_as_dict = [
        dict(
            username=row[0], name=row[1], message=row[2], debug_level=row[3], time=row[4]
        )
        for row in log_entries
    ]
    if not log_entries_as_dict:
        raise HTTPException(status_code=404, detail="User's log entries not found")
    return log_entries_as_dict
