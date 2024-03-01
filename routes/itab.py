from fastapi import APIRouter, HTTPException, Depends, Query
from logger import logging
from database import Log, User, get_db
from auth import get_current_user
from sqlalchemy.orm import Session
from sqlalchemy import String, cast, and_
import re

router = APIRouter()


@router.get("/log/{tag}={value}")
async def search_log_entries_by_request_body_value(tag: str, value: str, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    if tag == "username":
        log_entries = (db.query(Log.username, User.email, Log.request_body, Log.request_rels, Log.date,Log.approvement_data, Log.obwii, Log.depth_, Log.limit_)
                       .join(User,Log.username == User.username)
                       .filter(Log.username == value)
                       .order_by(Log.date.desc()).all())
        logging.info(f"{value}", extra={'user': current_user, 'table': 'itap',
                                        'action': 'поиск пользователя по username'})
    elif tag == "username_partial":
        log_entries = (
            db.query(Log.username, User.email, Log.request_body, Log.request_rels, Log.date, Log.approvement_data,
                     Log.obwii, Log.depth_, Log.limit_)
            .join(User, Log.username == User.username)
            .filter(cast(Log.username, String)
                    .contains(value))
            .order_by(Log.date.desc()).all())
        logging.info(f"{value}", extra={'user': current_user, 'table': 'itap',
                                        'action': 'поиск пользователя по username_partial'})
    elif tag == "iin":
        log_entries = (db.query(Log.username, User.email, Log.request_body, Log.request_rels, Log.date,Log.approvement_data, Log.obwii, Log.depth_, Log.limit_)
                       .join(User,Log.username == User.username)
                       .filter(cast(Log.request_body, String)
                               .contains(value)).order_by(Log.date.desc()).all())
        logging.info(f"{value}", extra={'user': current_user, 'table': 'itap',
                                        'action': 'поиск по иин'})
    elif tag == "fullname":
        log_entries = (db.query(Log.username, User.email, Log.request_body, Log.request_rels, Log.date,Log.approvement_data, Log.obwii, Log.depth_, Log.limit_)
                       .join(User, Log.username == User.username)
                       .filter(cast(User.email, String)
                               .contains(value))
                       .order_by(Log.date.desc()).all())
        logging.info(f"{value}", extra={'user': current_user, 'table': 'itap',
                                        'action': 'поиск пользователя по фио'})
    elif tag == "fullname_full":
        log_entries = (db.query(Log.username, User.email, Log.request_body, Log.request_rels, Log.date,Log.approvement_data, Log.obwii, Log.depth_, Log.limit_)
                       .join(User, Log.username == User.username)
                       .filter(User.email == value)
                       .order_by(Log.date.desc()).all())
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


def to_camel_case(s):
    return ' '.join(word.capitalize() for word in s.split())

@router.get("/log/search_fio/")
async def get_log_fullname_log_entries(lname: str = Query(None),
                                          mname : str = Query(None),
                                          fname : str = Query(None),
                                          full_lname: str = Query(None),
                                          full_mname: str = Query(None),
                                          full_fname: str = Query(None),
                                          current_user : str = Depends(get_current_user),
                                          db : Session = Depends(get_db)):

    # empty list to store filter conditions
    filter_conditions = []
    if fname:
        filter_conditions.append(cast(Log.request_body, String).contains(fname))
    if mname:
        filter_conditions.append(cast(Log.request_body, String).contains(mname))
    if lname:
        filter_conditions.append(cast(Log.request_body, String).contains(lname))

    if full_fname :
        search_term = r'\y{}\y'.format(re.escape(full_fname))
        filter_conditions.append(Log.request_body.op('~')(search_term))
    if full_mname :
        search_term = r'\y{}\y'.format(re.escape(full_mname))
        filter_conditions.append(Log.request_body.op('~')(search_term))
    if full_lname :
        search_term = r'\y{}\y'.format(re.escape(full_lname))
        filter_conditions.append(Log.request_body.op('~')(search_term))

    # Combine filter conditions using AND
    combined_filter = and_(*filter_conditions)

    log_entries = (db.query(Log.username, User.email, Log.request_body, Log.request_rels, Log.date,Log.approvement_data, Log.obwii, Log.depth_, Log.limit_)
                       .join(User, Log.username == User.username)
                                 .filter(combined_filter)
                                 .order_by(Log.date.desc()).all())

    log_entries_as_dict = [
        dict(
            username=row[0], email=row[1], request_body=row[2], request_rels=row[3],
            date=row[4], approvement_data=row[5], obwii=row[6], depth_=row[7], limit_=row[8]
        )
        for row in log_entries
    ]
    if not log_entries_as_dict:
        raise HTTPException(status_code=404, detail="User's log entries not found")
    logging.info(f"{lname} {fname} {mname}", extra={'user': current_user,'table': 'itab','action': 'поиск фл по фио'})
    return log_entries_as_dict



