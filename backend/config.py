import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'elbigodom_secret_key')
    JWT_SECRET = os.getenv('JWT_SECRET', 'elbigodom_jwt_secret')
    JWT_EXPIRATION = timedelta(hours=24)

    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'elbigodom')
    }