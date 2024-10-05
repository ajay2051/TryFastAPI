import logging
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from itsdangerous import URLSafeTimedSerializer

from app import models
from app.auth import schemas
from app.auth.get_create_user import get_user_by_email
from app.db_connection import get_db
from app.models import UserRole

# to get a string like this run:
# openssl rand -hex 32

load_dotenv()
SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = float(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS = float(os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    """
    Verify Password with user entered password
    :param plain_password:
    :param hashed_password:
    :return:
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    Hashes the password
    :param password:
    :return:
    """
    return pwd_context.hash(password)


def authenticate_user(db: Session, email: str, password: str):
    """
    Authenticate user by comparing user entered email and password with database email and password
    :param db:
    :param email:
    :param password:
    :return:
    """
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Create Access Token for Authenticated User
    :param data:
    :param expires_delta:
    :return:
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict):
    """
    Create Refresh Token for Authenticated User
    :param data:
    :return:
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_refresh_token(token: str):
    """
    Verify Refresh Token for Authenticated User
    :param token:
    :return:
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        token_type: str = payload.get("type")
        if email is None or token_type != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        token_data = schemas.TokenData(email=email)
        return token_data
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")


def blacklist_token(db: Session, token: str):
    """
    Blacklisted Token after logout
    :param db:
    :param token:
    :return:
    """
    db_token = models.BlacklistedToken(token=token)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token


def is_token_blacklisted(db: Session, token: str) -> bool:
    """
    Checks if token is blacklisted
    :param db:
    :param token:
    :return:
    """
    return db.query(models.BlacklistedToken).filter(models.BlacklistedToken.token == token).first() is not None


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Get Current User
    :param token:
    :param db:
    :return:
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception

    if is_token_blacklisted(db, token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been blacklisted")

    user = get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    """
    Get Current Active User
    :param current_user:
    :return:
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def is_admin(user: schemas.User):
    """
    Checks if user is admin
    :param user:
    :return:
    """
    return user.role == UserRole.ADMIN


async def get_current_admin_user(current_user: schemas.User = Depends(get_current_active_user)):
    """
    Get Current Admin User
    :param current_user:
    :return:
    """
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user


serializer = URLSafeTimedSerializer(secret_key=SECRET_KEY, salt="email-configuration")


def create_url_safe_token(data: dict):
    """
    Create URL safe token
    :param data:
    :return:
    """
    token = serializer.dumps(data)
    return token


def decode_urlsafe_token(token: str):
    """
    Decode URL safe token
    :param token:
    :return:
    """
    try:
        token_data = serializer.loads(token)
        return token_data
    except Exception as e:
        logging.error(e)
