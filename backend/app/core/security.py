from datetime import datetime, timedelta, UTC
from cryptography.fernet import Fernet
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings
import base64
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def create_access_token(subject: str, minutes: int = 1440) -> str:
    exp = datetime.now(UTC) + timedelta(minutes=minutes)
    return jwt.encode({"sub": subject, "exp": exp}, settings.app_secret_key, algorithm=ALGORITHM)


def verify_admin(username: str, password: str) -> bool:
    return username == settings.admin_username and password == settings.admin_password


def _fernet() -> Fernet:
    key = base64.urlsafe_b64encode(hashlib.sha256(settings.session_secret_key.encode()).digest())
    return Fernet(key)


def encrypt_session(raw: str) -> str:
    return _fernet().encrypt(raw.encode()).decode()


def decrypt_session(token: str) -> str:
    return _fernet().decrypt(token.encode()).decode()
