from fastapi import APIRouter, Depends, HTTPException, status
from database import get_db
from sqlalchemy.orm import Session
from schemas.customers import CustomerCreate, CustomerRead, CustomerUpdate
from services import customers as customer_service
from dependencies import get_current_user, require_role

router = APIRouter(
    prefix="/customers",
    tags=["customers"],
    dependencies=[Depends(get_current_user)],  # must be logged in for every route below
)


@router.get(
    "/",
    response_model=list[CustomerRead],
    dependencies=[Depends(require_role("staff", "super_admin"))],
)
def list_customers(db: Session = Depends(get_db)):
    return customer_service.list_customers(db)


@router.get("/{customer_id}", response_model=CustomerRead)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    customer = customer_service.get_customer(db, customer_id)

    if current_user.role == "customer":
        # a plain customer may only view their own linked profile
        linked = getattr(current_user, "customer_profile", None)
        if not linked or linked.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not your customer profile",
            )

    return customer


@router.post(
    "/",
    response_model=CustomerRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("staff", "super_admin"))],
)
def create_customer(data: CustomerCreate, db: Session = Depends(get_db)):
    return customer_service.create_customer(db, data)


@router.put(
    "/{customer_id}",
    response_model=CustomerRead,
    dependencies=[Depends(require_role("staff", "super_admin"))],
)
def update_customer(customer_id: int, data: CustomerUpdate, db: Session = Depends(get_db)):
    return customer_service.update_customer(db, customer_id, data)


@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("staff", "super_admin"))],
)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    return customer_service.delete_customer(db, customer_id)