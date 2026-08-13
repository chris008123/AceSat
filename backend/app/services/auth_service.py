"""Auth service — Backend_architecture.txt §10 "Authentication Service:
Registration, Login, Password management."
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.user import User
from app.services.security import create_access_token, hash_password, verify_password
from app.utils.errors import AuthError, ValidationAPIError


def register_user(db: Session, email: str, password: str) -> User:
    existing = db.query(User).filter_by(email=email).first()
    if existing is not None:
        raise ValidationAPIError("An account with this email already exists")

    user = User(email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter_by(email=email).first()
    if user is None or not verify_password(password, user.password_hash):
        raise AuthError("Invalid credentials")
    return user


def issue_token_for(user: User) -> str:
    return create_access_token(user.id)
