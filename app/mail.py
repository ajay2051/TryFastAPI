from pathlib import Path
from typing import List

from fastapi import FastAPI
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from config import settings

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent

mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER=Path(BASE_DIR, "templates"),
)

mail = FastMail(config=mail_config)


# @app.post("/email")
# async def create_message(recipients:List[str], subject: str, body:str):
#
#     message = MessageSchema(
#         subject=subject,
#         recipients=recipients,
#         body=body,
#         subtype=MessageType.html)
#     return message

    # fm = FastMail(mail_config)
    # await fm.send_message(message)
    # return JSONResponse(status_code=200, content={"message": "email has been sent"})

async def send_email_async(addresses: List[str], subject: str, body: str):
    message = MessageSchema(
        subject=subject,
        recipients=addresses,
        template_body={},
        body=body,
        subtype=MessageType.html
    )
    await mail.send_message(message, template_name="email_template.html")
