from fastapi import APIRouter, Depends, status
from database import get_db
from sqlalchemy.orm import Session
from schemas.library_rentals import LibraryRentalCreate, LibraryRentalRead, LibraryRentalUpdate
from services import library_rentals as library_rental_service

router = APIRouter(prefix="/library-rentals", tags=["library-rentals"])

@router.get("/", response_model=list[LibraryRentalRead])
def list_rentals(db: Session = Depends(get_db)):
    return library_rental_service.list_rentals(db)

@router.get("/{rental_id}", response_model=LibraryRentalRead)
def get_rental(rental_id: int, db: Session = Depends(get_db)):
    return library_rental_service.get_rental(db, rental_id)

@router.post("/", response_model=LibraryRentalRead, status_code=status.HTTP_201_CREATED)
def create_rental(data: LibraryRentalCreate, db: Session = Depends(get_db)):
    return library_rental_service.create_rental(db, data)

@router.put("/{rental_id}", response_model=LibraryRentalRead)
def update_rental(rental_id: int, data: LibraryRentalUpdate, db: Session = Depends(get_db)):
    return library_rental_service.update_rental(db, rental_id, data)

@router.delete("/{rental_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rental(rental_id: int, db: Session = Depends(get_db)):
    return library_rental_service.delete_rental(db, rental_id)
