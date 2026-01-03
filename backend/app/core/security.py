# app/core/security.py
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from app.core.config import settings


# -----------------------------
# Password hashing (ohne externe libs)
# Format: pbkdf2_sha256$<iters>$<salt_b64>$<hash_b64>
# -----------------------------
_PBKDF2_ITERS = 210_000
_SALT_BYTES = 16
_HASH_BYTES = 32


def _b64e(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode("utf-8").rstrip("=")


def _b64d(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


def hash_password(password: str) -> str:
    if not password:
        raise ValueError("Password must not be empty")

    salt = os.urandom(_SALT_BYTES)
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        _PBKDF2_ITERS,
        dklen=_HASH_BYTES,
    )
    return f"pbkdf2_sha256${_PBKDF2_ITERS}${_b64e(salt)}${_b64e(dk)}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algo, iters_s, salt_b64, hash_b64 = password_hash.split("$", 3)
        if algo != "pbkdf2_sha256":
            return False
        iters = int(iters_s)
        salt = _b64d(salt_b64)
        expected = _b64d(hash_b64)

        dk = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iters,
            dklen=len(expected),
        )
        return hmac.compare_digest(dk, expected)
    except Exception:
        return False


# -----------------------------
# JWT
# -----------------------------
def create_access_token(
    *,
    subject: str,
    tenant_id: str,
    role: str,
    expires_minutes: int = 15,
) -> tuple[str, int]:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=expires_minutes)

    payload: dict[str, Any] = {
        "sub": subject,
        "tenant_id": tenant_id,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "typ": "access",
    }

    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token, int((exp - now).total_seconds())


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as e:
        raise ValueError("Invalid token") from e


# -----------------------------
# Refresh token (plain token + DB hash)
# Hash = sha256( JWT_SECRET + ":" + refresh_token )
# -----------------------------
def create_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def hash_refresh_token(refresh_token: str) -> str:
    data = f"{settings.JWT_SECRET}:{refresh_token}".encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def verify_refresh_token(refresh_token: str, expected_hash: str) -> bool:
    return hmac.compare_digest(hash_refresh_token(refresh_token), expected_hash)
