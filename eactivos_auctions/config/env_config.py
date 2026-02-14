import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    EACTIVOS_LOGIN_EMAIL = os.getenv("EACTIVOS_LOGIN_EMAIL")
    EACTIVOS_LOGIN_PASSWORD = os.getenv("EACTIVOS_LOGIN_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
    DB_HOST = os.getenv("DB_HOST")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
