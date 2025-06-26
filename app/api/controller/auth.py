from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schema.base import PasswordResetRequest, PasswordResetVerify
from app.schema.base import UserCreate, UserLogin
from app.utils.database import get_db
from app.services.auth import create_user, login_user
from app.services.auth import get_user_by_email, generate_and_send_reset_code, verify_reset_code, update_user_password, clear_reset_code
from app.utils.custom_response import success_response, error_response
from app.schema.base import FirebaseTokenRequest
from app.services.auth import google_sign_in_sign_up
from app.services import get_current_user


async def email_password_auth(user: UserCreate, db: Session = Depends(get_db)) -> UserCreate:
    return await create_user(data=user, db=db)

async def signin_user(data: UserLogin, db: Session = Depends(get_db)) -> UserLogin:
    return await login_user(data=data, db=db)

async def google_handle(request: FirebaseTokenRequest, db: Session = Depends(get_db)):
    try:
        return await google_sign_in_sign_up(db, request.id_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during Google Sign-Up: {e}",
        )


async def forgot_password(payload: PasswordResetRequest, db: Session = Depends(get_db)):
    """
    Initiates the password reset process by sending a 6-digit code to the user's email.
    """
    user = get_user_by_email(db, payload.email)
    if not user:
        
        return {"message": "If a matching email address was found, a password reset code has been sent to your email."}
    
    # Call the CRUD function to generate, store, and send the code
    generate_and_send_reset_code(db, user) 
    return {"message": "Password reset code sent to your email."}

def reset_password(payload: PasswordResetVerify, db: Session = Depends(get_db)):
    # Verifies if a given reset code for an email is valid and not expired.

    if not verify_reset_code(db, payload.email, payload.code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset code.")
    
    # Update the user's password
    success = update_user_password(db, payload.email, payload.password)

    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to reset password.")
    
    # Clear the reset code after successful password change

    user = get_user_by_email(db, payload.email)
    if user:
        clear_reset_code(db, user)
    else:
        return error_response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="User not found.")

    if not clear_reset_code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to clear reset code after password change.")

    return success_response(status_code=status.HTTP_200_OK, message="Password reset successfully.")

async def get_user_profile(current_user=Depends(get_current_user)):
    return current_user