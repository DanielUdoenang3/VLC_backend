from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.models.base import User
from jose import jwt, JWTError
from datetime import datetime, timedelta
from app.utils.settings import settings
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.utils.custom_response import success_response,error_response

SECRET_KEY = settings.SECRET_KEY
JWT_ALGORITHM = settings.JWT_ALGORITHM
REFRESH_TOKEN_EXPIRES_IN = settings.REFRESH_TOKEN_EXPIRES_IN
ACCESS_TOKEN_EXPIRES_IN = settings.ACCESS_TOKEN_EXPIRES_IN


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return decoded
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None


def refresh_access_token(token: str):
    decoded = decode_access_token(token)
    if decoded:
        return create_access_token(data=decoded)
    return None