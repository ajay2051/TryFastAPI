from datetime import datetime, timedelta

import psycopg2
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app import models
# from app.auth.auth import clean_blacklisted_tokens
from config import settings

app = FastAPI()

load_dotenv()

DEV_DATABASE_URL = DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}" \
               f":{settings.database_port}/{settings.database_name}"
engine = create_engine(DEV_DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=True)  # dependency injection


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# def clean_blacklisted_tokens(db: Session, days: int = 7):
#     expiration_date = datetime.utcnow() - timedelta(days=days)
#     db.query(models.BlacklistedToken).filter(models.BlacklistedToken.blacklisted_on < expiration_date).delete()
#     db.commit()


@app.on_event("startup")
async def startup():
    app.db_connection = psycopg2.connect(DEV_DATABASE_URL)

    async def clean_tokens(days: int = 7):
        db = SessionLocal()
        try:
            expiration_date = datetime.utcnow() - timedelta(days=days)
            db.query(models.BlacklistedToken).filter(models.BlacklistedToken.blacklisted_on < expiration_date).delete()
            db.commit()
        finally:
            db.close()

    background_tasks = BackgroundTasks()
    background_tasks.add_task(clean_tokens)


@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()
