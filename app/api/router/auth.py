from fastapi import APIRouter
from app.api.controller.auth import email_password_auth, signin_user, google_handle, get_user_profile
from app.api.controller.auth import email_password_auth, signin_user
from app.api.controller.auth import forgot_password, reset_password


user_router = APIRouter(prefix="/auth", tags=["User and Google Auth"])

user_router.add_api_route(
    "/register",
    endpoint=email_password_auth,
    methods=["POST"],
    response_model=None,
    summary="Create a new user",
)

user_router.add_api_route(
    "/login",
    endpoint=signin_user,
    methods=["POST"],
    response_model=None,
    summary="Login a user",
)

user_router.add_api_route(
    "/continue-with-google",
    endpoint=google_handle,
    methods=["POST"],
    response_model=None,
    summary="Sign up and Sign in with Google"
)

user_router.add_api_route(
    "/forgot",
    endpoint=forgot_password,
    methods=["POST"],
    response_model=None,
    summary="Forgotten Password?"
)

user_router.add_api_route(
    "/reset-password",
    endpoint=reset_password,
    methods=["POST"],
    response_model=None,
    summary="Reset Password",
)

user_router.add_api_route(
    "/get_current_user",
    endpoint=get_user_profile,
    methods=["GET"],
    response_model=None,
    summary="Get Current User"
)