import os
from dotenv import load_dotenv

from sqlalchemy import create_engine, Column, Integer, String, DateTime, URL, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


load_dotenv()
DATABASE_URL = URL.create("postgresql",
                          username=os.getenv("username1"),
                          password=os.getenv("password1"),
                          host=os.getenv("host1"),
                          # port=os.getenv("port3", "5433"),
                          database=os.getenv("database1"))
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

DATABASE_URL2 = URL.create("postgresql",
                           username=os.getenv("username"),
                           password=os.getenv("password"),
                           host=os.getenv("host"),
                           # port=os.getenv("port3", "5434"),
                           database=os.getenv("database"))
# DATABASE_URL2=URL.create("postgresql",username="root",password="password",host="localhost",port="5434",database="simple_bank_2")
engine2 = create_engine(DATABASE_URL2)
SessionLocal2 = sessionmaker(autocommit=False, autoflush=False, bind=engine2)

DATABASE_URL3 = URL.create("postgresql",
                           username=os.getenv("username3"),
                           password=os.getenv("password3"),
                           host=os.getenv("host3"),
                           port=os.getenv("port3", "5444"),
                           database=os.getenv("database3"))
# DATABASE_URL2=URL.create("postgresql",username="root",password="password",host="localhost",port="5434",database="simple_bank_2")
engine3 = create_engine(DATABASE_URL3)

with engine3.connect() as connection:
    connection.execute(text("SET search_path TO simdata,public;"))

SessionLocal3 = sessionmaker(autocommit=False, autoflush=False, bind=engine3)

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


def get_db3():
    db = SessionLocal3()
    try:
        yield db
    finally:
        db.close()


class SimDataLog(Base):
    __tablename__ = "sim_audit_search"
    __table_args__ = {"schema": "simdata"}

    id = Column(Integer, primary_key=True, index=True)
    date_action = Column(DateTime)
    performer = Column(String)
    action = Column(Integer)
    member_name = Column(String)
    member_bin = Column(String)
    other_attributes = Column(String)


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
    date = Column(DateTime)
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

    time = Column(DateTime, primary_key=True, index=True)
    username = Column(String)
    debug_level = Column(Integer)
    message = Column(String)


class LogUser(Base):
    __tablename__ = "log_users"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    email = Column(String)


class Administration(Base):
    __tablename__ = "administration"

    id = Column(Integer, primary_key=True, index=True)
    dolzhnost = Column(String)
    podrazdeleniye = Column(String)
    fio = Column(String)
    iin = Column(String)
