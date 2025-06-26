from fastapi import status, HTTPException
from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session
import smtplib
from email.mime.text import MIMEText
import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials
from app.utils.settings import settings
from app.utils.pass_hash import hash_password
from app.models import base as models
from app.schema.base import UserCreate, UserLogin, AuthSuccessResponse
from app.utils.custom_response import error_response, success_response
from app.models.base import User
from app.utils.pass_hash import hash_password, verify_password
from app.utils.token import create_access_token

async def create_user(data: UserCreate, db) -> UserCreate:
    if not data.email or not data.username or not data.password:
        return error_response(status_code=status.HTTP_400_BAD_REQUEST, message= "Email, username, and password are required fields.")
    
    if not db:
        return error_response(status_code=status.HTTP_400_BAD_REQUEST, message= "Database session is not available.")
    
    existing_user = db.query(User).filter(
        (User.email == data.email) | (User.username == data.username)
    ).first()

    if existing_user:
        return error_response(status_code=status.HTTP_400_BAD_REQUEST, message= "User with this email or username already exists.")
    
    password_hashed = hash_password(data.password)

    if not password_hashed:
        return error_response(status_code=status.HTTP_400_BAD_REQUEST, message= "Password hashing failed.")

    new_user = User(
        email=data.email,
        username=data.username,
        hashed_password= password_hashed,
    )

    if not new_user:
        return error_response(status_code=status.HTTP_400_BAD_REQUEST, message= "User creation failed.")


    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token({"email": new_user.email})

    res = {
        "email": new_user.email,
        "username": new_user.username,
        "created_at": new_user.created_at,
        "updated_at": new_user.updated_at,
        "is_active": new_user.is_active,
        "access_token": access_token 
    }

    return success_response(status_code=status.HTTP_201_CREATED, message="User created successfully.", data=res)

async def login_user(data: UserLogin, db) -> UserLogin:
    if not data.email or not data.password:
        return error_response(status_code=status.HTTP_400_BAD_REQUEST, message="Email and password are required fields.")
    
    if not db:
        return error_response(status_code=status.HTTP_400_BAD_REQUEST, message="Database session is not available.")

    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.hashed_password):
        return error_response(status_code=status.HTTP_401_UNAUTHORIZED, message="Invalid email or password.")

    access_token = create_access_token({"email": user.email})

    res = {
        "email": user.email,
        "username": user.username,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "is_active": user.is_active,
        "access_token": access_token
    }

    return success_response(status_code=status.HTTP_200_OK, message="Login successful.", data=res)

def get_user_by_email(db: Session, email: str) -> models.User | None:
    """
    Retrieves a user from the database by their email address.
    """
    return db.query(models.User).filter(models.User.email == email).first()

def send_reset_email(to_email: str, code: str):
    subject = "Your Password Reset Code"
    # The email body now includes the 6-digit code
    body = f"Your password reset code from GIDE.AFRICA  is: {code}\n\n"
    #This code is valid for 20 minutes. Please enter this code on the password reset page to set your new password."
    
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.MAIL_USERNAME
    msg["To"] = to_email

    try:
        print("Connecting to email server...")
        with smtplib.SMTP_SSL(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
            server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            server.sendmail(settings.MAIL_USERNAME, to_email, msg.as_string())
        print("Email sent!")
    except Exception as e:
        print("Failed to send email:", e)

def set_password_reset_code(db: Session, user: models.User, code: str):
    """
    Sets a password reset code for a user with an expiry time.
    """
    user.reset_code = code
    # Set code expiry to 20 minutes from now
    user.reset_code_expiry = datetime.utcnow() + timedelta(minutes=20)
    db.add(user)
    db.commit()
    db.refresh(user)

def generate_and_send_reset_code(db: Session, user: models.User):
    """
    Generates a 6-digit reset code, stores it in the database,
    and sends it to the user's email.
    """
    reset_code = str(random.randint(100000, 999999))
    set_password_reset_code(db, user, reset_code)
    # Assuming send_reset_email takes 'to_email' and 'code' arguments
    send_reset_email(to_email=user.email, code=reset_code)

def verify_reset_code(db: Session, email: str, code: str) -> bool:
    """
    Verifies if a given reset code for an email is valid and not expired.
    """
    user = get_user_by_email(db, email)
    # Check if user exists, code matches, and code has not expired
    if not user or user.reset_code != code:
        return False
    if not user.reset_code_expiry or user.reset_code_expiry < datetime.utcnow():
        return False
    return True

def update_user_password(db: Session, email: str, new_password: str) -> bool:
    """
    Updates the user's password in the database.
    """
    user = get_user_by_email(db, email)
    if user:
        user.hashed_password = hash_password(new_password)
        db.commit()
        # db.refresh(table)
        return True
    return False

def clear_reset_code(db: Session, user: models.User) -> bool:
    """
    Clears the reset code and expiry time for a user.
    """
    try:
        user.reset_code = None
        user.reset_code_expiry = None
        db.add(user)
        db.commit()
        db.refresh(user)
        return True
    except Exception as e:
        print(e)
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to clear reset code."
        )

def initialize_firebase():
    firebase_credentials_path = settings.GOOGLE_APPLICATION_CREDENTIALS

    if not firebase_credentials_path:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS is not set in .env file")

    cred = credentials.Certificate(firebase_credentials_path)
    firebase_admin.initialize_app(cred)
    print("Firebase Admin SDK initialized successfully.")

# def handle_google_signin(db: Session, firebase_id_token: str) -> AuthSuccessResponse:
#         decoded_token = auth.verify_id_token(firebase_id_token)
#         email = decoded_token.get("email")

#         if not email:
#             raise HTTPException(status_code=400, detail="Email not found in Google token.")

#         user = db.query(User).filter(User.email == email).first()

#         if not user:
#             raise HTTPException(status_code=404, detail="User not found.")

#         access_token = create_access_token({"email": user.email})
        
#         return {
#             "id": user.id,
#             "email": user.email,
#             "username": user.username,
#             "access_token": access_token
#         }

# async def handle_google_signup(db: Session, firebase_id_token: str):
#     decoded_token = auth.verify_id_token(firebase_id_token)
#     email = decoded_token.get("email")
#     name = decoded_token.get("name") or "GoogleUser"

#     if not email:
#         raise HTTPException(status_code=400, detail="Email not found in Google token.")

#     existing_user = db.query(User).filter(User.email == email).first()
    
#     if existing_user:
#         raise HTTPException(status_code=409, detail="User already exists.")

#     dummy_password = hash_password(firebase_id_token[:12])  # Not used for login

#     new_user = User(
#         email=email,
#         username=name,
#         hashed_password=dummy_password
#     )
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)

#     access_token = create_access_token(data={"email": new_user.email})
    
#     return {
#         "id": new_user.id,
#         "email": new_user.email,
#         "username": new_user.username,
#         "access_token": access_token
#     }

async def google_sign_in_sign_up(db: Session, firebase_id_token: str):
    decoded_token = auth.verify_id_token(firebase_id_token)
    email = decoded_token.get("email")
    name = decoded_token.get("name") or "GoogleUser"

    if not email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found in Google token.")
    
    user = db.query(User).filter(User.email == email).first()

    if user:
        access_token = create_access_token({"email": user.email})
        
        res = {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "access_token": access_token
        }

        return success_response(
            status_code=status.HTTP_200_OK,
            message="Login In successfully",
            data=res
        )
    else:
        dummy_password = hash_password(firebase_id_token[:12])  # Not used for login

        new_user = User(
            email=email,
            username=name,
            hashed_password=dummy_password
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        access_token = create_access_token({"email": new_user.email})

        res={
            "id": new_user.id,
            "email": new_user.email,
            "username": new_user.username,
            "access_token": access_token
        }

        return success_response(
            status_code=status.HTTP_200_OK,
            message="User created successfully",
            data=res
        )