import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    EACTIVOS_LOGIN_EMAIL = os.getenv("EACTIVOS_LOGIN_EMAIL")
    EACTIVOS_LOGIN_PASSWORD = os.getenv("EACTIVOS_LOGIN_PASSWORD")
