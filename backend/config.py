# app/config.py
import os
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()

db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise ValueError("FATAL: DATABASE_URL environment variable is missing!")
CHECKPOINTER_DB_URI = db_url.replace("postgresql+psycopg://", "postgresql://")

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("FATAL: SECRET_KEY environment variable is missing!")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = timedelta(days=7)

COOKIE_NAME = "access_token"
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"   # True in prod (HTTPS)
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax")                    # "none" for cross-domain

CORS_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if origin.strip()]