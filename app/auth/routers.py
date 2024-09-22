from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from app.auth import auth, get_create_user, schemas
from app.auth.auth import blacklist_token
from app.db_connection import get_db
from app.models import UserRole

auth_router = APIRouter(
    tags=['auth']
)


@auth_router.post("/token/", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    It generates access token, refresh token after login
    :param form_data:
    :param db:
    :return: access_token, refresh_token, token_type
    """
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    refresh_token = auth.create_refresh_token(data={"sub": user.username})
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
    user = get_create_user.get_user_by_username(db, username=token_data.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    new_refresh_token = auth.create_refresh_token(data={"sub": user.username})
    return {"access_token": access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}


@auth_router.post("/create_users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create Users with any roles.
    :param user:
    :param db:
    :return: user
    """
    db_user = get_create_user.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return get_create_user.create_user(db=db, user=user)


@auth_router.post('create_admin_users/', response_model=schemas.User)
def create_admin_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create Admin Users
    :param user:
    :param db:
    :return: admin users.
    """
    db_user = get_create_user.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    user.role = UserRole.ADMIN.value
    return get_create_user.create_user(db=db, user=user)


@auth_router.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(auth.get_current_active_user)):
    """
    Current Active Logged-In Users
    :param current_user:
    :return: current user
    """
    return current_user


@auth_router.post("/logout")
async def logout(current_user: auth.schemas.User = Depends(auth.get_current_user), token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)):
    blacklist_token(db, token)
    return {"message": "Successfully logged out"}
