import secrets
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.config.settings import settings
from app.dependencies.services import get_user_service, get_email_service
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.schemas.email_schema import EmailSchema
from app.schemas.password_schema import ResetPasswordRequest, ResetPasswordResponse, ChangePasswordRequest, \
    ChangePasswordResponse
from app.schemas.token_schema import Token
from app.schemas.user_schema import UserCreateRequest, UserResponse
from app.services.email_service import EmailService
from app.services.user_service import UserService
from app.utils.auth_utils import create_access_token, authenticate_user, get_password_hash

router = APIRouter(tags=["Auth"])


@router.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        user_service: Annotated[UserService, Depends(get_user_service)]
):
    user = user_service.get_user_by_email(form_data.username)
    user = authenticate_user(user, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=UserResponse)
async def read_users_me(
        current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreateRequest,
                  user_service: Annotated[UserService, Depends(get_user_service)]) -> UserResponse:
    user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        date_of_birth=user_data.date_of_birth,
        email=user_data.email,
        password=get_password_hash(user_data.password),
        phone=user_data.phone,
        role="user"
    )
    created_user = user_service.save(user)
    return created_user


@router.post("/forgot-password")
async def reset_password(email_schema: EmailSchema,
                         user_service: Annotated[UserService, Depends(get_user_service)],
                         email_service: Annotated[EmailService, Depends(get_email_service)]):
    email = email_schema.email
    user = user_service.get_user_by_email(email)
    if user:
        reset_token = secrets.token_urlsafe(10)
        user.reset_token = reset_token
        user_service.save(user)

        subject = 'Reset Password'
        recipients = [email]
        message = f'''
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Reset Password</title>
            </head>
            <body>
                <h1>Reset Your Password</h1>
                <p>Click the link below to reset your password:</p>
                <a href="{settings.RESET_PASSWORD_URL}/{reset_token}">Reset Password</a>
            </body>
            </html>
            '''
        subtype = 'html'

        await email_service.send_message(subject, recipients, message, subtype)
        return {"message": "Email has been sent."}
    else:
        raise HTTPException(status_code=400, detail="User with given email not found")


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest,
                         user_service: Annotated[UserService, Depends(get_user_service)]):
    user = user_service.get_user_by_email(request.email)
    if user:
        user_service.reset_password(user, request.reset_token, request.new_password)
        return ResetPasswordResponse(success=True, message="Changed password succesfully")
    else:
        raise HTTPException(status_code=400, detail="User with given email not found")


@router.post("/change-password")
async def change_password(request: ChangePasswordRequest,
                          current_user: Annotated[User, Depends(get_current_active_user)],
                          user_service: Annotated[UserService, Depends(get_user_service)]):
    if user_service.change_password(current_user, request.old_password, request.new_password):
        return ChangePasswordResponse(success=True, message="Password changed successfully")
    else:
        raise HTTPException(status_code=400, detail="Invalid password")