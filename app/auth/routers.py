import os
from datetime import timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette import status

from app.auth import auth, get_create_user, schemas
from app.auth.auth import blacklist_token, create_url_safe_token, decode_urlsafe_token
from app.auth.dependencies import RoleChecker
from app.auth.schemas import EmailSchema, LoginData
from app.db_connection import get_db
from app.mail import send_email_async, mail
from app.models import UserRole

auth_router = APIRouter(
    tags=['auth']
)


# @auth_router.post('/send_email')
# async def send_email(email: EmailSchema):
#     emails = email.addresses
#     html = "<h1>Welcome</h1>"
#     message = create_message(
#         recipients=emails,
#         subject='Welcome to Nepal',
#         body=html,
#     )
#     await mail.send_message(message)
#     return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Email has been sent"})


@auth_router.post('/send_email/')
async def send_email(email: EmailSchema, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email_async, email.addresses, "Welcome to Nepal")
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Email sending has been scheduled"})


@auth_router.post("/token/", response_model=schemas.Token)
async def login_for_access_token(form_data: LoginData, db: Session = Depends(get_db)):
    """
    It generates access token, refresh token after login
    :param form_data:
    :param db:
    :return: access_token, refresh_token, token_type
    """
    user = auth.authenticate_user(db, form_data.email, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    refresh_token = auth.create_refresh_token(data={"sub": user.email})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@auth_router.post("/token/refresh/", response_model=schemas.TokenResponse)
async def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    """
    This function generates access_token using refresh token and users don't have to use their credentials.
    :param refresh_token:
    :param db:
    :return: new access token, refresh_token, token_type
    """
    token_data = auth.verify_refresh_token(refresh_token)
    user = get_create_user.get_user_by_email(db, email=token_data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    new_refresh_token = auth.create_refresh_token(data={"sub": user.username})
    return {"access_token": access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}


@auth_router.post("/create_users/",
                  # response_model=schemas.User # commented because response format is changed to custom dict
                  )
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create Users with any roles.
    :param user:
    :param db:
    :return: user
    """
    db_user = get_create_user.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")
    new_user = get_create_user.create_user(db=db, user=user)
    domain = os.environ.get('DOMAIN')
    token = create_url_safe_token({"email": user.email})
    link = f"https://{domain}/api/v1/auth/verify/{token}"
    html_message = f"""
    <h1>Verify your Email</h1>
    <p>Please click this <a href="{link}">link</a> to verify your email</p>
    """
    message = send_email_async(
        addresses=[user.email],
        subject="Verify Account",
        body=html_message,
    )
    await mail.send_message(message)
    return {
        "message": "Account Created! Check Email",
        "user": new_user
    }


@auth_router.post('create_admin_users/', response_model=schemas.User)
def create_admin_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create Admin Users
    :param user:
    :param db:
    :return: admin users.
    """
    db_user = get_create_user.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")
    user.role = UserRole.ADMIN.value
    return get_create_user.create_user(db=db, user=user)


@auth_router.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(auth.get_current_active_user), _: bool = Depends(RoleChecker(['admin']))):
    """
    Current Active Logged-In Users
    :param _: Checks Role for current user
    :param current_user: Currently logged-in user
    :return: current user
    """
    return current_user


@auth_router.post("/logout")
async def logout(current_user: auth.schemas.User = Depends(auth.get_current_user), token: str = Depends(auth.oauth2_scheme),
                 db: Session = Depends(get_db)):
    blacklist_token(db, token)
    return {"message": "Successfully logged out"}
