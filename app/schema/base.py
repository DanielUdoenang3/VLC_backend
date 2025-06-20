from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str 

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")

class PasswordResetVerify(BaseModel): # New schema for the /verify-code endpoint
    email: EmailStr = Field(..., example="user@example.com", description="User's email for password reset code verification")
    code: str = Field(..., min_length=6, max_length=6, example="123456", description="6-digit password reset code")
    password: str = Field(..., example="newpassword123", description="New password to set after code verification")

class FirebaseTokenRequest(BaseModel):
    id_token: str

class AuthSuccessResponse(BaseModel):
    user: UserResponse
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600  