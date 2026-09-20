from fastapi import APIRouter, Depends, status
from database import get_db
from sqlalchemy.orm import Session
from schemas.books import BookCreate, BookRead, BookUpdate
from services import books as book_service
from dependencies import get_current_user, require_role


router = APIRouter(prefix="/books", tags=["books"], dependencies=[Depends(get_current_user)])


@router.get("/", response_model=list[BookRead])
def list_books(db: Session = Depends(get_db)):
    return book_service.list_books(db)


@router.get("/{book_id}", response_model=BookRead)
def get_book(book_id: int, db: Session = Depends(get_db)):
    return book_service.get_book(db, book_id)


@router.post(
    "/",
    response_model=BookRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("staff", "super_admin"))],
)
def create_book(data: BookCreate, db: Session = Depends(get_db)):
    return book_service.create_book(db, data)


@router.put(
    "/{book_id}",
    response_model=BookRead,
    dependencies=[Depends(require_role("staff", "super_admin"))],
)
def update_book(book_id: int, data: BookUpdate, db: Session = Depends(get_db)):
    return book_service.update_book(db, book_id, data)


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("staff", "super_admin"))],
)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    return book_service.delete_book(db, book_id)