"""Security utilities — password hashing (bcrypt directly) and JWT
issuing/validation (python-jose), per Backend_architecture.txt §6 and
Database_design.txt §8 ("Secure passwords", "JWT tokens").

Uses the `bcrypt` package directly rather than through `passlib` —
`passlib`'s bcrypt backend has a known incompatibility with `bcrypt>=4.1`
(it probes a `__about__` attribute that no longer exists and mishandles a
72-byte test vector), so going straight to `bcrypt` avoids pinning to an
older, unmaintained bcrypt version just to keep passlib happy.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from uuid import UUID

import bcrypt
from jose import JWTError, jwt

from app.config.settings import settings

# bcrypt has a hard 72-byte input limit — truncate rather than error, a
# password that long is already well past any reasonable strength need.
_MAX_PASSWORD_BYTES = 72


def hash_password(password: str) -> str:
    truncated = password.encode("utf-8")[:_MAX_PASSWORD_BYTES]
    return bcrypt.hashpw(truncated, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    truncated = plain_password.encode("utf-8")[:_MAX_PASSWORD_BYTES]
    return bcrypt.checkpw(truncated, password_hash.encode("utf-8"))


def create_access_token(user_id: UUID) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expiration_minutes)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> UUID | None:
    """Returns the user_id encoded in the token, or None if the token is
    invalid/expired. Callers (the `get_current_user` dependency) turn a
    None into a 401 — this function itself stays a pure decode step.
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        subject = payload.get("sub")
        return UUID(subject) if subject else None
    except (JWTError, ValueError):
        return None

