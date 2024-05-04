from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import insert
from database import get_db, LogUser
import os
from dotenv import load_dotenv
router = APIRouter()

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dependency to get the current user from JWT token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login/")


class LoginData(BaseModel):
    username: str
    password: str


@router.post("/login/")
async def login(data: LoginData, db: Session = Depends(get_db)):
    user = db.query(LogUser).filter(LogUser.username == data.username).first()
    if not user or not pwd_context.verify(data.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


class SignUpData(BaseModel):
    username: str
    email: str
    password: str


@router.post("/signup/")
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


async def get_current_user(token: str = Depends(oauth2_scheme)):
    return verify_token(token)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()

    to_encode.update({"exp": None})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
