from fastapi import APIRouter, HTTPException, Depends, Response, Query
from logger import logging
from database import UsersLog, Cascade, Log, User, DossieLog, SimDataLog, get_db, get_db2, get_db3
from auth import get_current_user
from sqlalchemy.orm import Session
from sqlalchemy import String, cast, func, and_
import pandas as pd
import re
from datetime import datetime


router = APIRouter()


@router.get("/{requestname}/{tagname}={value}/download_excel")
async def download_excel(requestname: str,
                         tagname: str,
                         value: str,
                         start_date: datetime = Query(None),
                         end_date: datetime = Query(None),
                         current_user: str = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    if requestname == "log":
        req_type = 1
        if tagname == "fullname":
            log_entries = (db.query(Log.username, User.email, Log.request_body, Log.request_rels, Log.date, Log.approvement_data, Log.obwii, Log.depth_, Log.limit_)
                           .join(User, Log.username == User.username)
                           .filter(cast(User.email, String).contains(value)))
            logging.info(f"{value}", extra={'user': current_user,
                                            'table': 'itap',
                                            'action': 'скачал поиск пользователя по фио'})
        elif tagname == "username":
            log_entries = (db.query(Log.username, User.email, Log.request_body, Log.request_rels, Log.date, Log.approvement_data, Log.obwii, Log.depth_, Log.limit_)
                           .join(User, Log.username == User.username)
                           .filter(cast(User.username, String).contains(value)))
            logging.info(f"{value}", extra={'user': current_user,
                                            'table': 'itap',
                                            'action': 'скачал поиск пользователя по username'})
        elif tagname == "username_partial":
            log_entries = (
                db.query(Log.username, User.email, Log.request_body, Log.request_rels, Log.date, Log.approvement_data, Log.obwii, Log.depth_, Log.limit_)
                .join(User, Log.username == User.username)
                .filter(cast(Log.username, String).contains(value)))
            logging.info(f"{value}", extra={'user': current_user,
                                            'table': 'itap',
                                            'action': 'скачал поиск пользователя по username'})
        elif tagname == "iin":
            log_entries = (
                db.query(Log.username, User.email, Log.request_body, Log.request_rels, Log.date, Log.approvement_data,
                         Log.obwii, Log.depth_, Log.limit_)
                .join(User, Log.username == User.username)
                .filter(cast(Log.request_body, String)
                        .contains(value)))
            logging.info(f"{value}", extra={'user': current_user, 'table': 'itap',
                                            'action': 'скачал поиск по иин'})

        else:
            raise HTTPException(status_code=404, detail=f"Bad Request")

        if start_date:
            log_entries = log_entries.filter(Log.date >= start_date)
        if end_date:
            log_entries = log_entries.filter(Log.date <= end_date)

        log_entries = log_entries.order_by(Log.date.desc()).all()
    elif requestname == "user_log":
        req_type = 2
        if tagname == "username":
            log_entries = db.query(UsersLog.username, Cascade.name, UsersLog.message, UsersLog.debug_level,
                                   UsersLog.time).join(Cascade, UsersLog.username == Cascade.email).filter(
                UsersLog.username == value).all()
            logging.info(f"{value}", extra={'user': current_user, 'table': 'users_log_cascade',
                                            'action': 'скачал поиск пользователя по username'})
        elif tagname == "username_partial":
            log_entries = (
                db.query(UsersLog.username, Cascade.name, UsersLog.message, UsersLog.debug_level, UsersLog.time)
                .join(Cascade, UsersLog.username == Cascade.email)
                .filter(cast(UsersLog.username, String)
                        .contains(value)).all())
            logging.info(f"{value}", extra={'user': current_user, 'table': 'users_log_cascade',
                                            'action': 'скачал поиск пользователя по username'})
        elif tagname == "message":
            log_entries = db.query(UsersLog.username, Cascade.name, UsersLog.message, UsersLog.debug_level,
                                   UsersLog.time).join(Cascade, UsersLog.username == Cascade.email).filter(
                cast(UsersLog.message, String).contains(value)).all()
            logging.info(f"{value}", extra={'user': current_user, 'table': 'users_log_cascade',
                                            'action': 'скачал поиск по иин'})
        elif tagname == "fullname":
            log_entries = db.query(UsersLog.username, Cascade.name, UsersLog.message, UsersLog.debug_level,
                                   UsersLog.time).join(Cascade, UsersLog.username == Cascade.email).filter(
                cast(Cascade.name, String).contains(value)).all()
            logging.info(f"{value}", extra={'user': current_user, 'table': 'users_log_cascade',
                                            'action': 'скачал поиск пользователя по фио'})
        else:
            raise HTTPException(status_code=404, detail=f"Bad Request")

        if start_date:
            log_entries = log_entries.filter(cast(UsersLog.time, String) >= start_date)
        if end_date:
            log_entries = log_entries.filter(cast(UsersLog.time, String) <= end_date)

        log_entries = log_entries.order_by(UsersLog.time.desc()).all()
    else:
        raise HTTPException(status_code=404, detail=f"Bad Request")

    if req_type == 1:
        log_entries_as_dict = [
            dict(
                username=row[0], email=row[1], request_body=row[2], request_rels=row[3],
                date=row[4], approvement_data=row[5], obwii=row[6], depth_=row[7], limit_=row[8]
            )
            for row in log_entries
        ]
        for entry in log_entries_as_dict:
            entry['date'] = entry['date'].strftime('%Y-%m-%d %H:%M:%S')
    elif req_type == 2:
        log_entries_as_dict = [
            dict(
                username=row[0], name=row[1], message=row[2], debug_level=row[3], time=row[4]
            )
            for row in log_entries
        ]
    try:
        df = pd.DataFrame(log_entries_as_dict)
        excel_filename = "data.xlsx"
        df.to_excel(excel_filename, index=False)
        with open(excel_filename, "rb") as file:
            content = file.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read Excel file: {e}")

    return Response(content, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": "attachment;filename=data.xlsx"})


@router.get("/dossie_log/{tag}={value}/download")
async def download_excel_dossie_log(tag: str, value: str,
                                    start_date: datetime = Query(None),
                                    end_date: datetime = Query(None),
                                    current_user: str = Depends(get_current_user),
                                    db: Session = Depends(get_db2)):
    if tag == "username":
        log_entries = db.query(DossieLog).filter(DossieLog.user_name == value)
        logging.info(f"{value}", extra={'user': current_user,
                                        'table': 'dossie_log',
                                        'action': 'скачал поиск пользователя по user_name'})
    elif tag == "username_partial":
        log_entries = (db.query(DossieLog)
                       .filter(cast(DossieLog.user_name, String)
                               .contains(value))
                       .order_by(DossieLog.log_time.desc()))
        logging.info(f"{value}", extra={'user': current_user, 'table': 'dossie_log',
                                        'action': 'скачал поиск пользователя по user_name'})
    elif tag == "fullname":
        value = value.upper()
        log_entries = db.query(DossieLog).filter(func.concat(DossieLog.lname, ' ', DossieLog.fname, ' ', DossieLog.mname)
                                                 .contains(value)).order_by(DossieLog.log_time.desc())
        logging.info(f"{value}", extra={'user': current_user, 'table': 'dossie_log', 'action': 'скачал поиск пользователя по фио'})
    elif tag == "fullname_full":
        value = value.upper()
        log_entries = db.query(DossieLog).filter(func.concat(DossieLog.lname, ' ', DossieLog.fname, ' ', DossieLog.mname).contains(value)).order_by(DossieLog.log_time.desc())
        logging.info(f"{value}", extra={'user': current_user, 'table': 'dossie_log', 'action': 'скачал поиск пользователя по фио'})

    elif tag == "action":
        log_entries = db.query(DossieLog).filter(DossieLog.action.like(f'%{value}%'))
        logging.info(f"{value}", extra={'user': current_user, 'table': 'dossie_log', 'action': 'скачал поиск по иин'})

    if start_date:
        log_entries = log_entries.filter(DossieLog.log_time >= start_date)
    if end_date:
        log_entries = log_entries.filter(DossieLog.log_time <= end_date)

    log_entries = log_entries.order_by(DossieLog.log_time.desc()).all()

    log_entries_as_dict = [
        {
            "user_name": log.user_name,
            "lname": log.lname,
            "action": log.action,
            "fname": log.fname,
            "mname": log.mname,
            "log_time": log.log_time
        }
        for log in log_entries
    ]

    try:
        df = pd.DataFrame(log_entries_as_dict)
        excel_filename = "data.xlsx"
        df.to_excel(excel_filename, index=False)
        with open(excel_filename, "rb") as file:
            content = file.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read Excel file: {e}")

    return Response(content, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": "attachment;filename=data.xlsx"})


@router.get("/dossie_log/download/fio/")
async def get_dossie_fullname_log_entries(lname: str = Query(None),
                                          mname: str = Query(None),
                                          fname: str = Query(None),
                                          full_lname: str = Query(None),
                                          full_mname: str = Query(None),
                                          full_fname: str = Query(None),
                                          start_date: datetime = Query(None),
                                          end_date: datetime = Query(None),
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

    if full_fname:
        search_term = r'\y{}\y'.format(re.escape(full_fname))
        filter_conditions.append(DossieLog.action.op('~')(search_term))
    if full_mname:
        search_term = r'\y{}\y'.format(re.escape(full_mname))
        filter_conditions.append(DossieLog.action.op('~')(search_term))
    if full_lname:
        search_term = r'\y{}\y'.format(re.escape(full_lname))
        filter_conditions.append(DossieLog.action.op('~')(search_term))

    # Combine filter conditions using AND
    combined_filter = and_(*filter_conditions)

    log_entries = db.query(DossieLog).filter(combined_filter)

    if start_date:
        log_entries = log_entries.filter(DossieLog.log_time >= start_date)
    if end_date:
        log_entries = log_entries.filter(DossieLog.log_time <= end_date)

    log_entries = log_entries.order_by(DossieLog.log_time.desc()).all()

    log_entries_as_dict = [
        {
            "user_name": log.user_name,
            "lname": log.lname,
            "fname": log.fname,
            "mname": log.mname,
            "action": log.action,
            "log_time": log.log_time
        }
        for log in log_entries
    ]

    try:
        df = pd.DataFrame(log_entries_as_dict)
        excel_filename = "data.xlsx"
        df.to_excel(excel_filename, index=False)
        with open(excel_filename, "rb") as file:
            content = file.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read Excel file: {e}")
    logging.info(f"{lname} {fname} {mname}", extra={'user': current_user,
                                                    'table': 'dossie_log',
                                                    'action': 'скачал поиск фл по фио'})
    return Response(content, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": "attachment;filename=data.xlsx"})


@router.get("/log/download/search_fio/")
async def get_log_fullname_log_entries(lname: str = Query(None),
                                       mname: str = Query(None),
                                       fname: str = Query(None),
                                       full_lname: str = Query(None),
                                       full_mname: str = Query(None),
                                       full_fname: str = Query(None),
                                       start_date: datetime = Query(None),
                                       end_date: datetime = Query(None),
                                       current_user: str = Depends(get_current_user),
                                       db: Session = Depends(get_db)):

    # empty list to store filter conditions
    filter_conditions = []
    if fname:
        filter_conditions.append(cast(Log.request_body, String).contains(fname))
    if mname:
        filter_conditions.append(cast(Log.request_body, String).contains(mname))
    if lname:
        filter_conditions.append(cast(Log.request_body, String).contains(lname))

    if full_fname:
        search_term = r'\y{}\y'.format(re.escape(full_fname))
        filter_conditions.append(cast(Log.request_body, String).op('~')(search_term))
    if full_mname:
        search_term = r'\y{}\y'.format(re.escape(full_mname))
        filter_conditions.append(cast(Log.request_body, String).op('~')(search_term))
    if full_lname:
        search_term = r'\y{}\y'.format(re.escape(full_lname))
        filter_conditions.append(cast(Log.request_body, String).op('~')(search_term))

    # Combine filter conditions using AND
    combined_filter = and_(*filter_conditions)

    log_entries = (db.query(Log.username, User.email, Log.request_body, Log.request_rels, Log.date, Log.approvement_data, Log.obwii, Log.depth_, Log.limit_)
                   .join(User, Log.username == User.username)
                     .filter(combined_filter))
    if start_date:
        log_entries = log_entries.filter(Log.date >= start_date)
    if end_date:
        log_entries = log_entries.filter(Log.date <= end_date)

    log_entries = log_entries.order_by(Log.date.desc()).all()

    log_entries_as_dict = [
        dict(
            username=row[0], email=row[1], request_body=row[2], request_rels=row[3],
            date=row[4], approvement_data=row[5], obwii=row[6], depth_=row[7], limit_=row[8]
        )
        for row in log_entries
    ]
    for entry in log_entries_as_dict:
        entry['date'] = entry['date'].strftime('%Y-%m-%d %H:%M:%S')
    try:
        df = pd.DataFrame(log_entries_as_dict)
        excel_filename = "data.xlsx"
        df.to_excel(excel_filename, index=False)
        with open(excel_filename, "rb") as file:
            content = file.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read Excel file: {e}")

    return Response(content, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": "attachment;filename=data.xlsx"})


@router.get("/simdata/{tag}={value}/download")
async def download_excel_dossie_log(tag: str, value: str,
                                    start_date: datetime = Query(None),
                                    end_date: datetime = Query(None),
                                    current_user: str = Depends(get_current_user),
                                    db: Session = Depends(get_db3)):
    log_entries = (db.query(SimDataLog.date_action, SimDataLog.action, SimDataLog.member_bin, SimDataLog.member_name,
                            SimDataLog.performer, SimDataLog.other_attributes))
    if tag == "username":
        log_entries = log_entries.filter(SimDataLog.performer == value)
        logging.info(f"{value}",
                     extra={'user': current_user, 'table': 'simdata', 'action': 'поиск пользователя по username'})
    elif tag == "username_partial":
        log_entries = log_entries.filter(cast(SimDataLog.performer, String).contains(value))
        logging.info(f"{value}",
                     extra={'user': current_user, 'table': 'simdata', 'action': 'поиск пользователя по username'})
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
            performer=row[4], date=row[0], action=row[1], member_bin=row[2], member_name=row[3], other=row[5]
        )
        for row in log_entries
    ]
    try:
        df = pd.DataFrame(log_entries_as_dict)
        excel_filename = "data.xlsx"
        df.to_excel(excel_filename, index=False)
        with open(excel_filename, "rb") as file:
            content = file.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read Excel file: {e}")

    return Response(content, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": "attachment;filename=data.xlsx"})