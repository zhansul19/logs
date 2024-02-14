from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, DateTime, cast, select,  URL
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware


# SQLAlchemy Database Configuration
DATABASE_URL = "postgresql://root:password@localhost:5433/simple_bank"

# Create SQLAlchemy Engine
engine = create_engine(DATABASE_URL)

# Create a sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
# Create the table
Base.metadata.create_all(bind=engine)

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

# Define SQLAlchemy Model for the "users_log" table
class UsersLog(Base):
    __tablename__ = "users_log"

    time = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    debug_level = Column(Integer)
    message = Column(String)

class LogUser(Base):
    __tablename__ = "log_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    password = Column(String)
    email = Column(String)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# FastAPI app
app = FastAPI()

# CORS settings
origins = [
    "http://localhost:3000",
]
# Add CORS middleware to allow requests from specified origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
# JWT Settings
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dependency to verify hashed password
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# Generate JWT token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dependency to get the current user from JWT token
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login/")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    return verify_token(token)

# Verify JWT token
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

# Route to authenticate user and generate JWT token
@app.post("/login/")
async def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# Route to register a new user
@app.post("/signup/")
async def signup(username: str, email: str, password: str, db: Session = Depends(get_db)):
    # Check if the username already exists
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    # Hash the password
    hashed_password = pwd_context.hash(password)
    # Create the new user
    new_user = User(username=username, email=email, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}


# Route to retrieve all log entries
@app.get("/log/")
async def get_all_log_entries(db: Session = Depends(get_db)):
    log_entries=db.query(Log).all()
    return log_entries

# Route to retrieve log entries by username
# http://127.0.0.1:8000/log/
@app.get("/log/{username}")
async def get_log_entries_by_username(username: str, db: Session = Depends(get_db)):
    log_entries = db.query(Log).all()
    return log_entries

# Route to retrieve log entries by request body value
# http://127.0.0.1:8000/log/search/?value=040525651055,http://127.0.0.1:8000/log/search/?value=бегенов
@app.get("/log/search/")
async def search_log_entries_by_request_body_value(value: str, db: Session = Depends(get_db)):
    # log_entries = db.query(Log).filter(cast(Log.request_body, String).contains(value)).all()
    log_entries = db.query(Log).filter(cast(Log.request_body, String).contains(value)).all()
    if not log_entries:
        raise HTTPException(status_code=404, detail="Log entries not found")
    return log_entries



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


#
# # SQLAlchemy Database Configuration
# DATABASE_URL2 = URL.create(
#         "postgresql",
#         username="erdr_reader_kfm_db",
#         password="YrS$p1HUM@s2",
#         host="192.168.122.5",
#         database= "kfm_new"
#     )
#
# # Create SQLAlchemy Engine
# engine2 = create_engine(DATABASE_URL2)
#
# # Create a sessionmaker
# SessionLocal2 = sessionmaker(autocommit=False, autoflush=False, bind=engine2)
#
# # Dependency to get the database session
# def get_db2():
#     db = SessionLocal2()
#     try:
#         yield db
#     finally:
#         db.close()
#
# class DossieLog(Base):
#     __tablename__ = "logs"
#
#     id = Column(Integer, primary_key=True, index=True)
#     user_name = Column(String)
#     fname = Column(Integer)
#     lname = Column(Integer)
#     mname = Column(Integer)
#     action = Column(String)
# # Route to retrieve log entries by username from "users_log" table
# @app.get("/dossie_log/{user_name}")
# async def get_dossie_log_entries_by_username(user_name: str, db: Session = Depends(get_db2)):
#     log_entries = db.query(DossieLog).filter(DossieLog.user_name == user_name).all()
#     if not log_entries:
#         raise HTTPException(status_code=404, detail="User's log entries not found")
#     return log_entries
#
# # Route to search log entries by message from "users_log" table
# # http://127.0.0.1:8000/dossie_log/search/?action=150540008706
# @app.get("/dossie_log/search/")
# async def search_dossie_log_entries_by_cation(action: str, db: Session = Depends(get_db2)):
#     log_entries = db.query(DossieLog).filter(DossieLog.action.like(f'%{action}%')).all()
#     if not log_entries:
#         raise HTTPException(status_code=404, detail="Log entries not found")
#     return log_entries
