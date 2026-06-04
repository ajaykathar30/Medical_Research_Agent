# app/config.py
import os
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()

# config.py
CHECKPOINTER_DB_URI = os.getenv("DATABASE_URL").replace("postgresql+psycopg://", "postgresql://")

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")   # set a real one in .env
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = timedelta(days=7)

COOKIE_NAME = "access_token"
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"   # True in prod (HTTPS)
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax")                    # "none" for cross-domain