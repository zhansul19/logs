from fastapi import APIRouter, HTTPException, Depends, Query
from logger import logging
from database import SimDataLog, get_db3
from auth import get_current_user
from sqlalchemy.orm import Session
from sqlalchemy import String, cast
import re

router = APIRouter()


@router.get("/simdata/{tag}={value}/")
async def get_users_log_entries_by_username(tag: str,
                                            value: str,
                                            start_date: str = Query(None),
                                            end_date: str = Query(None),
                                            current_user: str = Depends(get_current_user),
                                            db: Session = Depends(get_db3)):
    log_entries = (db.query(SimDataLog.date_action,SimDataLog.action,SimDataLog.member_bin,SimDataLog.member_name,SimDataLog.performer,SimDataLog.other_attributes))
    if tag == "username":
        log_entries = log_entries.filter(SimDataLog.performer == value)
        logging.info(f"{value}", extra={'user': current_user, 'table': 'simdata', 'action': 'поиск пользователя по username'})
    elif tag == "username_partial":
        log_entries = log_entries.filter(cast(SimDataLog.performer, String).contains(value))
        logging.info(f"{value}", extra={'user': current_user, 'table': 'simdata', 'action': 'поиск пользователя по username'})
    elif tag == "member_name":
        log_entries = log_entries.filter(cast(SimDataLog.member_name, String).contains(value))
        logging.info(f"{value}", extra={'user': current_user, 'table': 'simdata', 'action': 'поиск по имени'})
    elif tag == "member_bin":
        log_entries = log_entries.filter(cast(SimDataLog.member_bin, String).contains(value))
        logging.info(f"{value}", extra={'user': current_user, 'table': 'simdata', 'action': 'поиск по иин'})

    # Filter by date range
    if start_date:
        log_entries = log_entries.filter(cast(SimDataLog.date_action, String) >= start_date)
    if end_date:
        log_entries = log_entries.filter(cast(SimDataLog.date_action, String) <= end_date)

    if start_date or end_date:
        log_entries = log_entries.order_by(SimDataLog.date_action.asc()).all()
    else:
        log_entries = log_entries.order_by(SimDataLog.date_action.desc()).all()

    log_entries_as_dict = [
        dict(
            performer=row[4], date=row[0], action=row[1], member_bin=row[2], member_name=row[3],  other=row[5]
        )
        for row in log_entries
    ]
    if not log_entries_as_dict:
        raise HTTPException(status_code=404, detail="User's log entries not found")
    return log_entries_as_dict