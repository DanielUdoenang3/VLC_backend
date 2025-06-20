from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError

from app.utils.token import decode_access_token
from app.models.base import User
from app.utils.database import get_db 
from app.utils.settings import settings

SECRET_KEY = settings.SECRET_KEY
JWT_ALGORITHM = settings.JWT_ALGORITHM
REFRESH_TOKEN_EXPIRES_IN = settings.REFRESH_TOKEN_EXPIRES_IN
ACCESS_TOKEN_EXPIRES_IN = settings.ACCESS_TOKEN_EXPIRES_IN


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme), db:Session= Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        if payload is None or not isinstance(payload, dict):
            raise credentials_exception
        user_email = payload.get("email")
        if user_email is None:
            raise credentials_exception
    except JWTError:
        return credentials_exception

    user = db.query(User).filter(User.email == user_email).first()
    if user is None:
        return credentials_exception
    return user