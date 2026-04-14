import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from .models import TokenPayload

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)


# ---------------------------------------------------------------------------
# JWT configuration  (read from env, with safe defaults for development)
# ---------------------------------------------------------------------------

JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "CHANGE_ME_IN_PRODUCTION_USE_A_LONG_RANDOM_STRING")
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


# ---------------------------------------------------------------------------
# Token creation
# ---------------------------------------------------------------------------

def create_access_token(
    user_id: int,
    user_type: str,
    role: str,
    client_id: Optional[int] = None,
) -> tuple[str, int]:
    """
    Returns (encoded_jwt, expires_in_seconds).
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": f"{user_type}:{user_id}",
        "user_id": user_id,
        "user_type": user_type,
        "role": role,
        "exp": expire,
    }
    if client_id is not None:
        payload["client_id"] = client_id

    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token, ACCESS_TOKEN_EXPIRE_MINUTES * 60


def create_refresh_token(
    user_id: int,
    user_type: str,
) -> tuple[str, datetime]:
    """
    Returns (encoded_jwt, expires_at_datetime).
    """
    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": f"{user_type}:{user_id}",
        "user_id": user_id,
        "user_type": user_type,
        "exp": expires_at,
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token, expires_at


# ---------------------------------------------------------------------------
# Token validation
# ---------------------------------------------------------------------------

def decode_access_token(token: str) -> TokenPayload:
    """
    Decodes and validates an access token.
    Raises JWTError on any failure.
    """
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    return TokenPayload(
        sub=payload["sub"],
        user_id=payload["user_id"],
        user_type=payload["user_type"],
        role=payload["role"],
        client_id=payload.get("client_id"),
        exp=payload["exp"],
    )


def decode_refresh_token(token: str) -> dict:
    """
    Decodes and validates a refresh token.
    Raises JWTError on any failure.
    """
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
