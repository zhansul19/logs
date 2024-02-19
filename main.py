from fastapi import FastAPI, HTTPException, Depends,Response
from sqlalchemy import create_engine, Column, Integer, String, DateTime, cast, select,  URL, insert
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
from enum import Enum

# SQLAlchemy Database Configuration
database_url=URL.create("postgresql",username="postgres",password="123",host="192.168.122.121",database="amigo")

# Create SQLAlchemy Engine
engine = create_engine(database_url)

# Create a sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class TagName(str, Enum):
    fullname = "fullname"
    username = "username"
    iin = "iin"
    
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

# Create the table
Base.metadata.create_all(bind=engine)

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
    "http://localhost:3001",
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

class LoginData(BaseModel):
    username: str
    password: str

# { body
#   "username": "example_user",
#   "password": "password123"
# }
# Login handler returns bearer token like
# {    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cC...",
#     "token_type": "bearer" }
@app.post("/login/")
async def login(data: LoginData, db: Session = Depends(get_db)):
    user = db.query(LogUser).filter(LogUser.username == data.username).first()
    print(user)
    if not user or not pwd_context.verify(data.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

class SignUpData(BaseModel):
    username: str
    email: str
    password: str


# {
#   "username": "example_user",
#   "email": "user@example.com",
#   "password": "password123"
# }

@app.post("/signup/")
async def signup(data: SignUpData, db: Session = Depends(get_db)):
    # Check if the username already exists
    if db.query(LogUser).filter(LogUser.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    # Hash the password
    hashed_password = pwd_context.hash(data.password)
    # Define the insert statement
    insert_stmt = insert(LogUser).values(username=data.username, email=data.email, password=hashed_password)
    # Execute the insert statement
    db.execute(insert_stmt)
    # Commit the transaction
    db.commit()
    return {"message": "User registered successfully"}



# Route to retrieve all log entries
@app.get("/log/")
async def get_all_log_entries(current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    log_entries = db.query(Log.username, User.email,Log.request_body,Log.request_rels,Log.date,Log.approvement_data,Log.obwii,Log.depth_,Log.limit_).join(User,Log.username == User.username).all()
    log_entries_as_dict = [
        dict(
            username=row[0], email=row[1], request_body=row[2], request_rels=row[3],
            date=row[4], approvement_data=row[5], obwii=row[6], depth_=row[7], limit_=row[8]
        )
        for row in log_entries
    ]

    return log_entries_as_dict

# Route to retrieve log entries by username
# http://127.0.0.1:8000/log/
@app.get("/log/{username}")
async def get_log_entries_by_username(username: str, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    log_entries = db.query(Log.username, User.email,Log.request_body,Log.request_rels,Log.date,Log.approvement_data,Log.obwii,Log.depth_,Log.limit_).join(User,Log.username == User.username).filter(Log.username == username).all()

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

# Route to retrieve log entries by request body value
# http://127.0.0.1:8000/log/search/?value=040525651055,http://127.0.0.1:8000/log/search/?value=бегенов
@app.get("/log/search/")
async def search_log_entries_by_request_body_value(value: str,current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    log_entries = db.query(Log.username, User.email,Log.request_body,Log.request_rels,Log.date,Log.approvement_data,Log.obwii,Log.depth_,Log.limit_).join(User,Log.username == User.username).filter(cast(Log.request_body, String).contains(value)).all()
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


# Route to retrieve log entries by username from "users_log" table
# http://127.0.0.1:8000/users_log/savasava
@app.get("/users_log/{username}")
async def get_users_log_entries_by_username(username: str,current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    log_entries = db.query(UsersLog).filter(UsersLog.username == username).all()
    if not log_entries:
        raise HTTPException(status_code=404, detail="User's log entries not found")
    return log_entries

# Route to search log entries by message from "users_log" table
#http://127.0.0.1:8000/users_log/search/?message=180
@app.get("/users_log/search/")
async def search_users_log_entries_by_message(message: str, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    log_entries = db.query(UsersLog).filter(UsersLog.message.contains(message)).all()
    if not log_entries:
        raise HTTPException(status_code=404, detail="Log entries not found")
    return log_entries

@app.get("/download_excel")
async def download_excel(current_user: str = Depends(get_current_user)):
    json_data={
        "username": "example_user",
        "password": "password123"
    }
    # Convert JSON data to pandas DataFrame
    try:
        if isinstance(json_data, dict):
            # If JSON data is a dictionary, transform it into a list of dictionaries
            json_data = [json_data]
        df = pd.DataFrame(json_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to convert JSON to DataFrame: {e}")

    # Save DataFrame as Excel file
    try:
        excel_filename = "data.xlsx"
        df.to_excel(excel_filename, index=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save DataFrame to Excel: {e}")

    # Read the Excel file
    try:
        with open(excel_filename, "rb") as file:
            content = file.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read Excel file: {e}")

    # Return the Excel file as a downloadable response
    return Response(content, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": "attachment;filename=data.xlsx"})

# SQLAlchemy Database Configuration
DATABASE_URL2 = URL.create(
        "postgresql",
        username="",
        password="",
        host="",
        database= ""
    )

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
    user_name = Column(String)
    fname = Column(Integer)
    lname = Column(Integer)
    mname = Column(Integer)
    action = Column(String)
# Route to retrieve log entries by username from "users_log" table
@app.get("/dossie_log/{user_name}")
async def get_dossie_log_entries_by_username(user_name: str, current_user: str = Depends(get_current_user), db: Session = Depends(get_db2)):
    log_entries = db.query(DossieLog).filter(DossieLog.user_name == user_name).all()
    if not log_entries:
        raise HTTPException(status_code=404, detail="User's log entries not found")
    return log_entries

# Route to search log entries by message from "users_log" table
# http://127.0.0.1:8000/dossie_log/search/?action=150540008706
@app.get("/dossie_log/search/")
async def search_dossie_log_entries_by_cation(action: str, current_user: str = Depends(get_current_user), db: Session = Depends(get_db2)):
    log_entries = db.query(DossieLog).filter(DossieLog.action.like(f'%{action}%')).all()
    if not log_entries:
        raise HTTPException(status_code=404, detail="Log entries not found")
    return log_entries

@app.get("/log/{tagname}={value}")
async def get_users_log_entries_by_tagname_value(tagname: TagName, value: str, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):

    if tagname.value == "fullname":
        log_entries = db.query(Log.username, User.email,Log.request_body,Log.request_rels,Log.date,Log.approvement_data,Log.obwii,Log.depth_,Log.limit_).join(User,Log.username == User.username).filter(cast(User.email, String).contains(value)).all()
    elif tagname.value == "username":
        log_entries = db.query(Log.username, User.email,Log.request_body,Log.request_rels,Log.date,Log.approvement_data,Log.obwii,Log.depth_,Log.limit_).join(User,Log.username == User.username).filter(cast(User.username, String).contains(value)).all()
    else: 
        raise HTTPException(status_code=404, detail="Bad Request")

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


@app.get("/log/{tagname}={value}/download_excel")
async def download_excel(tagname: str, value: str, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    if tagname == "fullname":
        log_entries = db.query(Log.username, User.email,Log.request_body,Log.request_rels,Log.date,Log.approvement_data,Log.obwii,Log.depth_,Log.limit_).join(User,Log.username == User.username).filter(cast(User.email, String).contains(value)).all()
    elif tagname == "username":
        log_entries = db.query(Log.username, User.email,Log.request_body,Log.request_rels,Log.date,Log.approvement_data,Log.obwii,Log.depth_,Log.limit_).join(User,Log.username == User.username).filter(cast(User.username, String).contains(value)).all()
    elif tagname == "iin":
        #log_entries = db.query(Log.username, User.email,Log.request_body,Log.request_rels,Log.date,Log.approvement_data,Log.obwii,Log.depth_,Log.limit_).join(User,Log.username == User.username).filter(cast(User.iin, String).contains(value)).all()
        print()
    else:
        raise HTTPException(status_code=404, detail=f"Bad Request")
    
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