"""`get_current_user` — the `Depends()` every protected route uses.
Reads the bearer token, decodes it, and loads the `User` row — so route
handlers just declare `user: User = Depends(get_current_user)` and never
touch JWT decoding themselves.
"""

from __future__ import annotations

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.services.security import decode_access_token
from app.utils.errors import AuthError

_bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise AuthError("Invalid or expired token")

    user = db.query(User).filter_by(id=user_id).first()
    if user is None:
        raise AuthError("User not found")

    return user
