from fastapi import APIRouter, Depends, HTTPException, status
from database import get_db
from sqlalchemy.orm import Session
from schemas.library_rentals import LibraryRentalCreate, LibraryRentalRead, LibraryRentalUpdate
from services import library_rentals as library_rental_service
from dependencies import get_current_user, require_role

router = APIRouter(
    prefix="/library-rentals",
    tags=["library-rentals"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/", response_model=list[LibraryRentalRead])
def list_rentals(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role == "customer":
        linked = getattr(current_user, "customer_profile", None)
        if not linked:
            return []
        return library_rental_service.list_rentals_for_customer(db, linked.customer_id)
    return library_rental_service.list_rentals(db)


@router.get("/{rental_id}", response_model=LibraryRentalRead)
def get_rental(rental_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    rental = library_rental_service.get_rental(db, rental_id)

    if current_user.role == "customer":
        linked = getattr(current_user, "customer_profile", None)
        if not linked or rental.customer_id != linked.customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not your rental",
            )

    return rental


@router.post(
    "/",
    response_model=LibraryRentalRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("staff", "super_admin"))],
)
def create_rental(data: LibraryRentalCreate, db: Session = Depends(get_db)):
    return library_rental_service.create_rental(db, data)


@router.put(
    "/{rental_id}",
    response_model=LibraryRentalRead,
    dependencies=[Depends(require_role("staff", "super_admin"))],
)
def update_rental(rental_id: int, data: LibraryRentalUpdate, db: Session = Depends(get_db)):
    return library_rental_service.update_rental(db, rental_id, data)


@router.delete(
    "/{rental_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("staff", "super_admin"))],
)
def delete_rental(rental_id: int, db: Session = Depends(get_db)):
    return library_rental_service.delete_rental(db, rental_id)