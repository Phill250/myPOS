from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user, require_role
from schemas.users import MeRead, UserCreate, UserCreateByAdmin, UserRead, UserUpdate
from services import auth_services
from services import users as user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    # public self-signup — always created as role="customer"
    return auth_services.register(db, data)


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    return auth_services.authenticate(db, form_data.username, form_data.password)


@router.get("/me", response_model=MeRead)
def read_me(current_user=Depends(get_current_user)):
    """Who am I? Used by the frontend right after login."""
    return current_user


@router.get(
    "/lookup",
    response_model=UserRead,
    dependencies=[Depends(require_role("staff", "super_admin"))],
)
def lookup_user(username: str, db: Session = Depends(get_db)):
    """Find an account by username — used by staff to link a customer's
    online account to their customer profile."""
    user = user_service.get_by_username(db, username.strip())
    return user


@router.get(
    "/",
    response_model=list[UserRead],
    dependencies=[Depends(require_role("super_admin"))],
)
def list_users(db: Session = Depends(get_db)):
    return user_service.list_users(db)


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # customers may only look themselves up; staff/admin can see anyone
    if current_user.role == "customer" and current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return user_service.get_user(db, user_id)


@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("super_admin"))],
)
def create_user(data: UserCreateByAdmin, db: Session = Depends(get_db)):
    return auth_services.create_user_as_admin(db, data)


@router.put(
    "/{user_id}",
    response_model=UserRead,
    dependencies=[Depends(require_role("super_admin"))],
)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db)):
    return user_service.update_user(db, user_id, data)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("super_admin"))],
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.user_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account",
        )
    return user_service.delete_user(db, user_id)
