from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
import hashlib

# Importing direct variables from config (backwards compatible setup)
from app.config import (
    SECRET_KEY, 
    ALGORITHM, 
    ACCESS_TOKEN_EXPIRE_MINUTES, 
    REFRESH_TOKEN_EXPIRE_DAYS
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -----------------------------
# Password helpers
# -----------------------------
def _normalize_password(password: str) -> str:
    if len(password.encode("utf-8")) > 72:
        return hashlib.sha256(password.encode()).hexdigest()
    return password


def hash_password(password: str) -> str:
    return pwd_context.hash(_normalize_password(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(
        _normalize_password(plain_password),
        hashed_password
    )


# -----------------------------
# JWT helpers (timezone-aware)
# -----------------------------
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update({
        "exp": expire,
        "type": "access"
    })

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
    )

    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# -----------------------------
# Password Reset Token Helpers
# -----------------------------
def create_password_reset_token(data: dict):
    to_encode = data.copy()

    # Reset tokens usually last longer (e.g., 30 minutes)
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)

    to_encode.update({
        "exp": expire,
        "type": "reset"
    })

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)