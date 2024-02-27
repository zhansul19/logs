from sqlalchemy import create_engine, Column, Integer, String, DateTime, cast, Enum, URL, insert
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# DATABASE_URL=URL.create("postgresql",username="postgres",password="123",host="192.168.122.121",port="5432",database="amigo")
DATABASE_URL=URL.create("postgresql",username="root",password="password",host="localhost",port="5433",database="simple_bank")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# DATABASE_URL2 = URL.create("postgresql",username="erdr_reader_kfm_db",password="YrS$p1HUM@s2",host="192.168.122.5",database= "kfm_new")
DATABASE_URL2=URL.create("postgresql",username="root",password="password",host="localhost",port="5434",database="simple_bank_2")
engine2 = create_engine(DATABASE_URL2)
SessionLocal2 = sessionmaker(autocommit=False, autoflush=False, bind=engine2)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
def get_db2():
    db = SessionLocal2()
    try:
        yield db
    finally:
        db.close()

class DossieLog(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String)
    fname = Column(Integer)
    lname = Column(Integer)
    mname = Column(Integer)
    action = Column(String)
    log_time = Column(DateTime)

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
    username = Column(String)
    email = Column(String)

class Cascade(Base):
    __tablename__ = "cascade_credentials"

    name = Column(String)
    email = Column(String, primary_key=True, index=True)

# Define SQLAlchemy Model for the "users_log" table
class UsersLog(Base):
    __tablename__ = "users_log_cascade"

    time = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    debug_level = Column(Integer)
    message = Column(String)

class LogUser(Base):
    __tablename__ = "log_users"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    email = Column(String)
