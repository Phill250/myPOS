from sqlalchemy.orm import Session
from schemas.library_rentals import LibraryRentalCreate, LibraryRentalUpdate
from repositories.library_rentals import library_rental_repository
from fastapi import HTTPException, status

def get_rental(db: Session, id: int): 
    rental = library_rental_repository.get(db, id)
    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Rental record with id {id} not found"
        )
    return rental

def list_rentals(db: Session):
    return library_rental_repository.get_all(db)

def create_rental(db: Session, data: LibraryRentalCreate): 
    return library_rental_repository.create(db, data.model_dump())

def update_rental(db: Session, rental_id: int, data: LibraryRentalUpdate): 
    rental = get_rental(db, rental_id)
    
    if data.actual_return is not None and rental.actual_return is None:
        for item in rental.items:
            if item.book:
                item.book.library_stock += 1
                
    return library_rental_repository.update(db, rental, data.model_dump(exclude_unset=True))

def delete_rental(db: Session, rental_id: int): 
    rental = get_rental(db, rental_id)
    return library_rental_repository.delete(db, rental)
