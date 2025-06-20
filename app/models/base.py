from sqlalchemy import Column, DateTime, Enum, String, Integer as Boolean

from app.models.base_model import BaseModel
from datetime import datetime

class User(BaseModel):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    reset_code = Column(String, nullable=True) # Stores the 6-digit code
    reset_code_expiry = Column(DateTime, nullable=True) # Stores the expiration timestamp for the code
