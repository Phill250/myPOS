from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from database import get_db
from sqlalchemy.orm import Session
from schemas.users import UserCreate, UserCreateByAdmin, UserRead, UserUpdate
from services import users as user_service
from services import auth_services
from dependencies import get_current_user, require_role

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    # public self-signup — always created as role="customer"
    return auth_services.register(db, data)


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return auth_services.authenticate(db, form_data.username, form_data.password)


@router.get("/", response_model=list[UserRead], dependencies=[Depends(require_role("super_admin"))])
def list_users(db: Session = Depends(get_db)):
    return user_service.list_users(db)


@router.get("/{user_id}", response_model=UserRead, dependencies=[Depends(get_current_user)])
def get_user(user_id: int, db: Session = Depends(get_db)):
    return user_service.get_user(db, user_id)


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_role("super_admin"))])
def create_user(data: UserCreateByAdmin, db: Session = Depends(get_db)):
    return auth_services.create_user_as_admin(db, data)


@router.put("/{user_id}", response_model=UserRead, dependencies=[Depends(require_role("super_admin"))])
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db)):
    return user_service.update_user(db, user_id, data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(require_role("super_admin"))])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    return user_service.delete_user(db, user_id)