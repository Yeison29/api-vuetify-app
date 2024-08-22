from fastapi_mail import ConnectionConfig
from dotenv import load_dotenv
import os

load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv('EMAIL'),
    MAIL_PASSWORD=os.getenv('EMAIL_PASSWORD'),
    MAIL_FROM=os.getenv('EMAIL'),
    MAIL_PORT=os.getenv('EMAIL_PORT'),
    MAIL_SERVER=os.getenv('EMAIL_SERVE'),
    MAIL_FROM_NAME="AGRO-WEB",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)
