from pydantic_settings import BaseSettings
from decouple import config
from pathlib import Path

# Use this to build paths inside the project
BASE_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):
    """Class to hold application's config values."""

    SECRET_KEY: str = config("SECRET_KEY")
    JWT_ALGORITHM: str = config("JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRES_IN: int = config("ACCESS_TOKEN_EXPIRES_IN")
    REFRESH_TOKEN_EXPIRES_IN: int = config("REFRESH_TOKEN_EXPIRES_IN")

    FE_URL: str = config("FE_URL")

    # Database configurations
    DB_HOST: str = config("DB_HOST")
    DB_PORT: int = config("DB_PORT", cast=int)
    DB_USER: str = config("DB_USER")
    DB_PASSWORD: str = config("DB_PASSWORD")
    DB_NAME: str = config("DB_NAME")
    DB_TYPE: str = config("DB_TYPE")
    DB_URL: str = config("DB_URL")

    MAIL_USERNAME: str = config("MAIL_USERNAME")
    MAIL_PASSWORD: str = config("MAIL_PASSWORD")
    MAIL_FROM: str = config("MAIL_FROM")
    MAIL_PORT: int = config("MAIL_PORT")
    MAIL_SERVER: str = config("MAIL_SERVER")
    
    GOOGLE_APPLICATION_CREDENTIALS: str = config("GOOGLE_APPLICATION_CREDENTIALS")
    OPENAI_API_KEY: str = config("OPENAI_API_KEY")
    GEMINI_API_KEY: str = config("GEMINI_API_KEY")

settings = Settings()