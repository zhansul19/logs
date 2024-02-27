from fastapi import APIRouter, HTTPException, Depends, Response, Query
from logger import logging
from database import get_db2, DossieLog
from auth import get_current_user
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

router = APIRouter()

@router.get("/dossie_log/{tag}={value}")
async def get_dossie_log_entries(tag: str, value: str, current_user: str = Depends(get_current_user),
                                            db: Session = Depends(get_db2)):
    if tag == "username":
        log_entries = db.query(DossieLog).filter(DossieLog.user_name == value).order_by(DossieLog.log_time.desc()).all()
        logging.info(f"{value}",extra={'user': current_user, 'table': 'dossie_log', 'action': 'поиск пользователя по user_name'})
    elif tag == "fullname":
        value=value.upper()
        log_entries = db.query(DossieLog).filter(func.concat(DossieLog.lname,' ',DossieLog.fname,' ',DossieLog.mname).contains(value)).order_by(DossieLog.log_time.desc()).all()
        logging.info(f"{value}",extra={'user': current_user, 'table': 'dossie_log', 'action': 'поиск пользователя по фио'})
    elif tag == "action":
        log_entries = db.query(DossieLog).filter(DossieLog.action.like(f'%{value}%')).order_by(DossieLog.log_time.desc()).all()
        logging.info(f"{value}",extra={'user': current_user, 'table': 'dossie_log', 'action': 'поиск по иин'})

    if not log_entries:
        raise HTTPException(status_code=404, detail="User's log entries not found")
    return log_entries

# http://127.0.0.1:8000/dossie_log/fio/?lname=СҰЛТАН&fname=ЖАНСАЯ&mname=БАУЫРЖАНҚЫЗЫ
@router.get("/dossie_log/fio/")
async def get_dossie_fullname_log_entries(lname: str = Query(None),
                                          mname: str = Query(None),
                                          fname: str = Query(None),
                                          current_user: str = Depends(get_current_user),
                                          db: Session = Depends(get_db2)):

    # empty list to store filter conditions
    filter_conditions = []
    if fname:
        filter_conditions.append(DossieLog.action.like(f'%{fname}%'))
    if mname:
        filter_conditions.append(DossieLog.action.like(f'%{mname}%'))
    if lname:
        filter_conditions.append(DossieLog.action.like(f'%{lname}%'))

    # Combine filter conditions using AND
    combined_filter = and_(*filter_conditions)

    log_entries = db.query(DossieLog).filter(combined_filter).order_by(DossieLog.log_time.desc()).all()

    if not log_entries:
        raise HTTPException(status_code=404, detail="User's log entries not found")

    logging.info(f"{lname} {fname} {mname}", extra={'user': current_user,'table': 'dossie_log','action': 'поиск фл по фио'})
    return log_entries

