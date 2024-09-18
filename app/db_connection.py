import psycopg2
from dotenv import load_dotenv
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

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


@app.on_event("startup")
async def startup():
    app.db_connection = psycopg2.connect(DEV_DATABASE_URL)


@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()
