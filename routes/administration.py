from fastapi import APIRouter, HTTPException, Depends
from database import UsersLog, Administration, get_db, Log
from auth import get_current_user
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/risks/{request_name}/")
async def get_log_entries(request_name: str,
                          current_user: str = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    if request_name == "log":
        source = "itap"
        log_entries = (
            db.query(Log.date, Log.username, Administration.iin, Administration.fio)
            .join(Administration, Log.obwii.like('%' + Administration.iin + '%'))
        ).all()
    elif request_name == "users_log":
        source = "cascade"
        log_entries = (
            db.query(UsersLog.time, UsersLog.username, Administration.iin, Administration.fio)
            .join(Administration, UsersLog.message.like('%' + Administration.iin + '%'))
        ).all()

    log_entries_as_dict = [
        dict(
            date=row[0], username=row[1], iin=row[2], fio=row[3], source=source
        )
        for row in log_entries
    ]

    if not log_entries_as_dict:
        raise HTTPException(status_code=404, detail="User's log entries not found")

    return log_entries_as_dict


@router.get("/risks/{request_name}/{tag}={value}/")
async def get_log_entries(request_name: str,
                          value: str,
                          tag: str,
                          current_user: str = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    source = ""
    if request_name == "log":
        source = "itap"
        log_entries = (
            db.query(Log.date, Log.username, Administration.iin, Administration.fio)
            .join(Administration, Log.obwii.like('%' + Administration.iin + '%'))
        )
        if tag == "iin":
            log_entries = log_entries.filter(Administration.iin.contains(value)).all()
        elif tag == "fio":
            log_entries = log_entries.filter(Administration.fio.contains(value)).all()
    elif request_name == "users_log":
        source = "cascade"
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
            date=row[0], username=row[1], iin=row[2], fio=row[3], source=source
        )
        for row in log_entries
    ]

    if not log_entries_as_dict:
        raise HTTPException(status_code=404, detail="User's log entries not found")

    return log_entries_as_dict
