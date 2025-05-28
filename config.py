import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DB_USER=os.getenv('DB_USER')
    DB_PASSWORD=os.getenv('DB_PASSWORD')
    DB_HOST=os.getenv('DB_HOST')
    DB_PORT=os.getenv('DB_PORT')
    DB_NAME=os.getenv('DB_NAME')
    JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY')
    JWT_ALGORITHM=os.getenv('JWT_ALGORITHM')
    ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))
    REFRESH_TOKEN_EXPIRE_MINUTES=int(os.getenv('REFRESH_TOKEN_EXPIRE_MINUTES'))
    ALLOWED_ORIGINS=[origin.strip() for origin in os.getenv('ALLOWED_ORIGINS').split(",") if origin.strip()]
    
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
