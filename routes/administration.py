from fastapi import APIRouter, HTTPException, Depends, Query
from database import UsersLog, Administration, get_db
from auth import get_current_user
from sqlalchemy.orm import Session
import psycopg2

router = APIRouter()

@router.get("/users_log/administration/")
async def get_log_entries(current_user: str = Depends(get_current_user),
                          db: Session = Depends(get_db)):

    conn = psycopg2.connect(
        dbname="simple_bank",
        user="root",
        password="password",
        host="localhost",
        port="5433"
    )

    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT ul."time", ul.username, a.iin, a.fio
            FROM users_log ul
            JOIN administration a ON ul.message LIKE '%' || a.iin || '%'
        """)
        rows = cur.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")
    finally:
        cur.close()
        conn.close()

    log_entries_as_dict = [
        dict(
            time=row[0], name=row[1], iin=row[2], fio=row[3], source="cascade"
        )
        for row in rows
    ]

    if not log_entries_as_dict:
        raise HTTPException(status_code=404, detail="User's log entries not found")

    return log_entries_as_dict


@router.get("/log/administration/")
async def get_log_entries(current_user: str = Depends(get_current_user),
                          db: Session = Depends(get_db)):

    conn = psycopg2.connect(
        dbname="simple_bank",
        user="root",
        password="password",
        host="localhost",
        port="5433"
    )

    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT l.date,l.username ,l.request_body,a.fio  
                FROM log l 
            inner join administration a on  ARRAY_TO_STRING(l.request_body, ',') = a.iin
        """)
        rows = cur.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")
    finally:
        cur.close()
        conn.close()

    log_entries_as_dict = [
        dict(
            time=row[0], name=row[1], iin=row[2][0], fio=row[3], source="itab"
        )
        for row in rows
    ]

    if not log_entries_as_dict:
        raise HTTPException(status_code=404, detail="User's log entries not found")

    return log_entries_as_dict

# @router.get("/combined_log_entries/")
# async def get_combined_log_entries(current_user: str = Depends(get_current_user),
#                                     db: Session = Depends(get_db)):
#
#     conn = psycopg2.connect(
#         dbname="simple_bank",
#         user="root",
#         password="password",
#         host="localhost",
#         port="5433"
#     )
#
#     cur = conn.cursor()
#
#     combined_log_entries = []
#
#     try:
#         # Query for users_log/administration
#         cur.execute("""
#             SELECT ul."time", ul.username, a.iin, a.fio
#             FROM users_log ul
#             JOIN administration a ON ul.message LIKE '%' || a.iin || '%'
#         """)
#         rows = cur.fetchall()
#
#         log_entries_as_dict = [
#             dict(
#                 time=row[0], name=row[1], iin=row[2], fio=row[3], source="cascade"
#             )
#             for row in rows
#         ]
#         combined_log_entries.extend(log_entries_as_dict)
#
#         # Query for log/administration
#         cur.execute("""
#             SELECT l.date,l.username ,l.request_body,a.fio
#             FROM log l
#             INNER JOIN administration a ON ARRAY_TO_STRING(l.request_body, ',') = a.iin
#         """)
#         rows = cur.fetchall()
#
#         log_entries_as_dict = [
#             dict(
#                 time=row[0], name=row[1], iin=row[2][0], fio=row[3], source="itab"
#             )
#             for row in rows
#         ]
#         combined_log_entries.extend(log_entries_as_dict)
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error: {e}")
#     finally:
#         cur.close()
#         conn.close()
#
#     if not combined_log_entries:
#         raise HTTPException(status_code=404, detail="Combined log entries not found")
#
#     return combined_log_entries