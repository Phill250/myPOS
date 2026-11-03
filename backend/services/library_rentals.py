from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.customers import Customer
from models.users import User
from repositories.library_rentals import library_rental_repository
from schemas.library_rentals import LibraryRentalCreate, LibraryRentalUpdate


def get_rental(db: Session, id: int):
    rental = library_rental_repository.get(db, id)
    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rental record with id {id} not found",
        )
    return rental


def list_rentals(db: Session):
    return library_rental_repository.get_all(db)


def list_rentals_for_customer(db: Session, customer_id: int):
    return library_rental_repository.get_all_for_customer(db, customer_id)


def create_rental(db: Session, data: LibraryRentalCreate):
    if not db.get(Customer, data.customer_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Customer with id {data.customer_id} does not exist.",
        )
    if not db.get(User, data.user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Staff member with user_id {data.user_id} does not exist.",
        )
    return library_rental_repository.create(db, data.model_dump())


def _restock(rental, direction: int):
    for item in rental.items:
        if item.book:
            item.book.library_stock += direction


def update_rental(db: Session, rental_id: int, data: LibraryRentalUpdate):
    rental = get_rental(db, rental_id)
    values = data.model_dump(exclude_unset=True)

    was_out = rental.actual_return is None
    will_be_out = values.get("actual_return", rental.actual_return) is None

    if was_out and not will_be_out:
        _restock(rental, +1)  # books came back
    elif not was_out and will_be_out:
        # a return was undone (e.g. recorded by mistake) — books are out again
        for item in rental.items:
            if item.book and item.book.library_stock < 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"'{item.book.title}' has no free copy to re-issue",
                )
        _restock(rental, -1)

    return library_rental_repository.update(db, rental, values)


def delete_rental(db: Session, rental_id: int):
    rental = get_rental(db, rental_id)
    if rental.actual_return is None:
        _restock(rental, +1)  # cancelling an open loan frees its copies
    return library_rental_repository.delete(db, rental)
