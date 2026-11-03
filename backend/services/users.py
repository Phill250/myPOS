from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from core.security import hash_password
from repositories.users import user_repository
from schemas.users import UserUpdate

VALID_ROLES = {"customer", "staff", "super_admin"}


def get_user(db: Session, id: int):
    user = user_repository.get_by_id(db, id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} not found"
        )
    return user


def get_by_username(db: Session, username: str):
    user = user_repository.get_by_username(db, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No account with username '{username}'",
        )
    return user


def list_users(db: Session):
    return user_repository.get_all(db)


def update_user(db: Session, user_id: int, data: UserUpdate):
    user = get_user(db, user_id)
    values = data.model_dump(exclude_unset=True)

    if "username" in values and values["username"] != user.username:
        if user_repository.get_by_username(db, values["username"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )

    if "role" in values and values["role"] not in VALID_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role must be one of: {', '.join(sorted(VALID_ROLES))}",
        )

    # The model has no `password` column — hash it into password_hash,
    # otherwise the new password would be silently thrown away.
    password = values.pop("password", None)
    if password:
        values["password_hash"] = hash_password(password)

    return user_repository.update(db, user, values)


def delete_user(db: Session, user_id: int):
    user = get_user(db, user_id)
    return user_repository.delete(db, user)
