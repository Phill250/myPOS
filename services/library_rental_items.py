from sqlalchemy.orm import Session
from schemas.library_rental_items import LibraryRentalItemCreate, LibraryRentalItemUpdate
from repositories.books import book_repository
from repositories.library_rental_items import library_rental_item_repository
from fastapi import HTTPException, status

def get_rental_item(db: Session, id: int): 
    item = library_rental_item_repository.get(db, id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Rental item record with id {id} not found"
        )
    return item

def list_rental_items(db: Session):
    return library_rental_item_repository.get_all(db)


def create_rental_item(db: Session, data: LibraryRentalItemCreate):
    book = book_repository.get(db, data.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
        
    if book.library_stock < 1:
        raise HTTPException(status_code=400, detail="This book is currently fully checked out")
        
    book.library_stock -= 1
    db.commit() 
    
    return library_rental_item_repository.create(db, data.model_dump())

def update_rental_item(db: Session, rental_item_id: int, data: LibraryRentalItemUpdate): 
    item = get_rental_item(db, rental_item_id)
    return library_rental_item_repository.update(db, item, data.model_dump(exclude_unset=True))

def delete_rental_item(db: Session, rental_item_id: int): 
    item = get_rental_item(db, rental_item_id)
    return library_rental_item_repository.delete(db, item)
