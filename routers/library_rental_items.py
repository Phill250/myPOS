from fastapi import APIRouter, Depends, status
from database import get_db
from sqlalchemy.orm import Session
from schemas.library_rental_items import LibraryRentalItemCreate, LibraryRentalItemRead, LibraryRentalItemUpdate
from services import library_rental_items as library_rental_item_service
from dependencies import get_current_user, require_role

router = APIRouter(
    prefix="/library-rental-items",
    tags=["library-rental-items"],
    dependencies=[Depends(get_current_user)],
)

@router.get("/", response_model=list[LibraryRentalItemRead])
def list_rental_items(db: Session = Depends(get_db)):
    return library_rental_item_service.list_rental_items(db)

@router.get("/{rental_item_id}", response_model=LibraryRentalItemRead)
def get_rental_item(rental_item_id: int, db: Session = Depends(get_db)):
    return library_rental_item_service.get_rental_item(db, rental_item_id)

@router.post(
    "/",
    response_model=LibraryRentalItemRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("staff", "super_admin"))],
)
def create_rental_item(data: LibraryRentalItemCreate, db: Session = Depends(get_db)):
    return library_rental_item_service.create_rental_item(db, data)

@router.put(
    "/{rental_item_id}",
    response_model=LibraryRentalItemRead,
    dependencies=[Depends(require_role("staff", "super_admin"))],
)
def update_rental_item(rental_item_id: int, data: LibraryRentalItemUpdate, db: Session = Depends(get_db)):
    return library_rental_item_service.update_rental_item(db, rental_item_id, data)

@router.delete(
    "/{rental_item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("staff", "super_admin"))],
)
def delete_rental_item(rental_item_id: int, db: Session = Depends(get_db)):
    return library_rental_item_service.delete_rental_item(db, rental_item_id)