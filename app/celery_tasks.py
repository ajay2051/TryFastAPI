from celery import Celery
from asgiref.sync import async_to_sync
from app.mail import send_email_async, mail

c_app = Celery()

c_app.config_from_object('config')  # config is config.py i.e filename


@c_app.task
def send_email_celery(addresses: list[str], subject: str, html_message: str):
    message = send_email_async(
        addresses=addresses,
        subject=subject,
        body=html_message,
    )
    async_to_sync(mail.send_message)(message)
    print("Email Sent")
