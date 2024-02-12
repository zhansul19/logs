
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, DateTime, cast, select
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# SQLAlchemy Database Configuration
DATABASE_URL = "postgresql://root:password@localhost:5433/simple_bank"

# Create SQLAlchemy Engine
engine = create_engine(DATABASE_URL)

# Create a sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# SQLAlchemy Base
Base = declarative_base()

# Define SQLAlchemy Model
class Log(Base):
    __tablename__ = "log"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    request_body = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
    limit_ = Column(Integer)
    depth_ = Column(Integer)
    request_rels = Column(String)
    obwii = Column(String)
    approvement_data = Column(String)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String)


# Create the table
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI()

# Route to retrieve all log entries
@app.get("/log/")
async def get_all_log_entries(db: Session = Depends(get_db)):
    log_entries = db.query(Log).all()
    return log_entries

# Route to retrieve log entries by username
@app.get("/log/{username}")
async def get_log_entries_by_username(username: str, db: Session = Depends(get_db)):
    stmt = select(User).join(Log, User.username == Log.username)
    log_entries = db.query(stmt)
    return log_entries

# Route to retrieve log entries by request body value
# http://127.0.0.1:8000/log/search/?value=040525651055,http://127.0.0.1:8000/log/search/?value=бегенов
@app.get("/log/search/")
async def search_log_entries_by_request_body_value(value: str, db: Session = Depends(get_db)):
    log_entries = db.query(Log).filter(cast(Log.request_body, String).contains(value)).all()
    if not log_entries:
        raise HTTPException(status_code=404, detail="Log entries not found")
    return log_entries


# Define SQLAlchemy Model for the "users_log" table
class UsersLog(Base):
    __tablename__ = "users_log"

    time = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    debug_level = Column(Integer)
    message = Column(String)
# Route to retrieve log entries by username from "users_log" table
# http://127.0.0.1:8000/users_log/savasava
@app.get("/users_log/{username}")
async def get_users_log_entries_by_username(username: str, db: Session = Depends(get_db)):
    log_entries = db.query(UsersLog).filter(UsersLog.username == username).all()
    if not log_entries:
        raise HTTPException(status_code=404, detail="User's log entries not found")
    return log_entries

# Route to search log entries by message from "users_log" table
#http://127.0.0.1:8000/users_log/search/?message=180
@app.get("/users_log/search/")
async def search_users_log_entries_by_message(message: str, db: Session = Depends(get_db)):
    log_entries = db.query(UsersLog).filter(UsersLog.message.contains(message)).all()
    if not log_entries:
        raise HTTPException(status_code=404, detail="Log entries not found")
    return log_entries



# SQLAlchemy Database Configuration
DATABASE_URL2 = "postgresql://erdr_reader_kfm_db:YrS$p1HUM@s2@192.168.122.5:5432/kfm_new"

# Create SQLAlchemy Engine
engine2 = create_engine(DATABASE_URL2)

# Create a sessionmaker
SessionLocal2 = sessionmaker(autocommit=False, autoflush=False, bind=engine2)

# Dependency to get the database session
def get_db2():
    db = SessionLocal2()
    try:
        yield db
    finally:
        db.close()

class DossieLog(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    fname = Column(Integer)
    action = Column(String)
# Route to retrieve log entries by username from "users_log" table
@app.get("/dossie_log/{username}")
async def get_dossie_log_entries_by_username(username: str, db: Session = Depends(get_db2)):
    log_entries = db.query(DossieLog).filter(DossieLog.username == username).all()
    if not log_entries:
        raise HTTPException(status_code=404, detail="User's log entries not found")
    return log_entries

# Route to search log entries by message from "users_log" table
@app.get("/dossie_log/search/")
async def search_dossie_log_entries_by_message(action: str, db: Session = Depends(get_db2)):
    log_entries = db.query(DossieLog).filter(DossieLog.message.contains(action)).all()
    if not log_entries:
        raise HTTPException(status_code=404, detail="Log entries not found")
    return log_entries
