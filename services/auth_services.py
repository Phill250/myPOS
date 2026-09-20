from typing import Any
import jwt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

from repositories.users import user_repository
from schemas.users import UserCreate


def register(db: Session, data: UserCreate):
    """Public self-registration. Always creates a plain 'customer' account,
    regardless of any role passed in the request."""
    if user_repository.get_by_username(db, data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="username exists",
        )

    values = data.model_dump(exclude={"password", "role"})
    values["password_hash"] = hash_password(data.password)
    values["role"] = "customer"
    return user_repository.create(db, values)


def create_user_as_admin(db: Session, data: UserCreate):
    """Used only by the super-admin-only endpoint. Allows setting any role
    (e.g. staff, super_admin) since the caller is already verified as super_admin."""
    if user_repository.get_by_username(db, data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="username exists",
        )

    values = data.model_dump(exclude={"password"})
    values["password_hash"] = hash_password(data.password)
    return user_repository.create(db, values)


def authenticate(db: Session, username: str, password: str):
    user = user_repository.get_by_username(db, username)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {
        "access_token": create_access_token(user.user_id),
        "token_type": "bearer",
    }


def get_user_from_token(db: Session, token: str):
    try:
        payload: dict[str, Any] = decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    subject = payload.get("sub")
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = int(subject)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = user_repository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user