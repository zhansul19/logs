from fastapi import APIRouter, HTTPException, Depends
from database import UsersLog, Administration, get_db, Log, get_db2, DossieLog
from auth import get_current_user
from sqlalchemy.orm import Session
import csv
from sqlalchemy import or_

router = APIRouter()


@router.get("/risks/users_log/")
async def get_risk_entries(current_user: str = Depends(get_current_user),
                           db: Session = Depends(get_db)):

    log_entries = (
        db.query(UsersLog.time, UsersLog.username, Administration.iin, Administration.fio)
        .join(Administration, UsersLog.message.like('%' + Administration.iin + '%'))
    ).all()

    log_entries_as_dict = [
        dict(
            time=row[0], username=row[1], iin=row[2], fio=row[3]
        )
        for row in log_entries
    ]

    if not log_entries_as_dict:
        raise HTTPException(status_code=404, detail="User's log entries not found")

    return log_entries_as_dict


@router.get("/risks/log/")
async def get_risk_entries(current_user: str = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    log_entries = (
        db.query(Log.date, Log.username, Administration.iin, Administration.fio)
        .join(Administration, Log.obwii.like('%' + Administration.iin + '%'))
    ).all()

    log_entries_as_dict = [
        dict(
            date=row[0], username=row[1], iin=row[2], fio=row[3]
        )
        for row in log_entries
    ]

    if not log_entries_as_dict:
        raise HTTPException(status_code=404, detail="User's log entries not found")

    return log_entries_as_dict


@router.get("/risks/users_log/{tag}={value}/")
async def get_risk_cascade_log_entries(value: str,
                                       tag: str,
                                       current_user: str = Depends(get_current_user),
                                       db: Session = Depends(get_db)):

    log_entries = (
        db.query(UsersLog.time, UsersLog.username, Administration.iin, Administration.fio)
        .join(Administration, UsersLog.message.like('%' + Administration.iin + '%'))
    )
    if tag == "iin":
        log_entries = log_entries.filter(Administration.iin.contains(value)).all()
    elif tag == "fio":
        log_entries = log_entries.filter(Administration.fio.contains(value)).all()
    else:
        raise HTTPException(status_code=404, detail="User's log entries not found")

    log_entries_as_dict = [
        dict(
            time=row[0], username=row[1], iin=row[2], fio=row[3]
        )
        for row in log_entries
    ]

    if not log_entries_as_dict:
        raise HTTPException(status_code=404, detail="User's log entries not found")

    return log_entries_as_dict


@router.get("/risks/log/{tag}={value}/")
async def get_risk_itab_log_entries(value: str,
                                    tag: str,
                                    current_user: str = Depends(get_current_user),
                                    db: Session = Depends(get_db)):
    log_entries = (
        db.query(Log.date, Log.username, Administration.iin, Administration.fio)
        .join(Administration, Log.obwii.like('%' + Administration.iin + '%'))
    )
    if tag == "iin":
        log_entries = log_entries.filter(Administration.iin.contains(value)).all()
    elif tag == "fio":
        log_entries = log_entries.filter(Administration.fio.contains(value)).all()

    else:
        raise HTTPException(status_code=404, detail="User's log entries not found")

    log_entries_as_dict = [
        dict(
            date=row[0], username=row[1], iin=row[2], fio=row[3]
        )
        for row in log_entries
    ]

    if not log_entries_as_dict:
        raise HTTPException(status_code=404, detail="User's log entries not found")

    return log_entries_as_dict


@router.get("/risks/dossie_log/iin={value}/")
async def get_risk_entries_dossie(value: str,
                                  current_user: str = Depends(get_current_user),
                                  db: Session = Depends(get_db2)):
    # Read the CSV file and extract ИИН values
    iin_values = []
    fioval = []
    # with open('C:/Users/User6/Desktop/logs/log/administration2.csv', 'r', encoding='utf-8') as file:
    with open('root/log_new/logs/administration2.csv', 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        next(csv_reader)  # Skip the header row
        for row in csv_reader:
            for key, val in row.items():
                if value in val:
                    iin_values.append(value)
                    fioval.append(row['ИИН'])
                    fioval.append(row['ФИО'])
                    break

    if iin_values[0] == value:
        like_conditions = DossieLog.action.like(f'%{value}%')

    log_entries = db.query(DossieLog).filter(DossieLog.action.like('Поиск%')).filter(like_conditions).all()

    log_entries_as_dict = [
        dict(
            log_time=row.log_time, user_name=row.lname+" "+row.fname, iin=fioval[0], fio=fioval[1]
        )
        for row in log_entries
    ]

    if not log_entries_as_dict:
        raise HTTPException(status_code=404, detail="User's log entries not found")

    return log_entries_as_dict


@router.get("/risks/dossie_log/")
async def get_risk_entries_all_dossie(current_user: str = Depends(get_current_user),
                                      db: Session = Depends(get_db2)):
    # Read the CSV file and extract ИИН values
    iin_values = []
    iin_to_fio_mapping = {}

    # with open('C:/Users/User6/Desktop/logs/log/administration2.csv', 'r', encoding='utf-8') as file:
    with open('root/log_new/logs/administration2.csv', 'r', encoding='utf-8') as file:
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
    log_entries = db.query(DossieLog).filter(DossieLog.action.like('Поиск%')).filter(combined_condition).all()

    log_entries_as_dict = [
        dict(
            log_time=row.log_time, user_name=row.lname + " " + row.fname, iin=row.action, fio=""
        )
        for row in log_entries
    ]

    for entry in log_entries_as_dict:
        for iin, fio in iin_to_fio_mapping.items():
            if iin in entry["iin"]:
                entry["fio"] = fio
                entry["iin"] = iin

    if not log_entries_as_dict:
        raise HTTPException(status_code=404, detail="User's log entries not found")

    return log_entries_as_dict
