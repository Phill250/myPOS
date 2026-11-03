"""Single loan-line endpoints. For the normal library desk flow, use
services/checkout.py instead — it creates the loan and all its books in one
transaction."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.books import Book
from models.library_rental_items import LibraryRentalItem
from models.library_rentals import LibraryRental
from repositories.library_rental_items import library_rental_item_repository
from schemas.library_rental_items import (
    LibraryRentalItemCreate,
    LibraryRentalItemUpdate,
)


def get_rental_item(db: Session, id: int):
    item = library_rental_item_repository.get(db, id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rental item record with id {id} not found",
        )
    return item


def list_rental_items(db: Session):
    return library_rental_item_repository.get_all(db)


def _get_book_or_404(db: Session, book_id: int) -> Book:
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


def _take_copy(book: Book):
    if book.library_stock < 1:
        raise HTTPException(
            status_code=400, detail="This book is currently fully checked out"
        )
    book.library_stock -= 1


def create_rental_item(db: Session, data: LibraryRentalItemCreate):
    rental = db.get(LibraryRental, data.rental_id)
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")
    if rental.actual_return is not None:
        raise HTTPException(
            status_code=400, detail="This rental has already been returned"
        )

    book = _get_book_or_404(db, data.book_id)
    _take_copy(book)

    item = LibraryRentalItem(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_rental_item(db: Session, rental_item_id: int, data: LibraryRentalItemUpdate):
    item = get_rental_item(db, rental_item_id)
    values = data.model_dump(exclude_unset=True)

    new_book_id = values.get("book_id", item.book_id)
    still_out = item.rental is not None and item.rental.actual_return is None

    if new_book_id != item.book_id and still_out:
        if item.book:
            item.book.library_stock += 1
        new_book = _get_book_or_404(db, new_book_id)
        try:
            _take_copy(new_book)
        except HTTPException:
            db.rollback()
            raise

    return library_rental_item_repository.update(db, item, values)


def delete_rental_item(db: Session, rental_item_id: int):
    item = get_rental_item(db, rental_item_id)
    # if the book is still out on this loan, removing the line puts it back
    if item.book and item.rental is not None and item.rental.actual_return is None:
        item.book.library_stock += 1
    return library_rental_item_repository.delete(db, item)
