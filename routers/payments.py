from fastapi import APIRouter, Depends, status
from database import get_db
from sqlalchemy.orm import Session
from schemas.payments import PaymentCreate, PaymentRead, PaymentUpdate
from services import payments as payment_service
from dependencies import get_current_user, require_role

router = APIRouter(
    prefix="/payments",
    tags=["payments"],
    dependencies=[Depends(get_current_user)],
)

@router.get("/", response_model=list[PaymentRead], dependencies=[Depends(require_role("staff", "super_admin"))])
def list_payments(db: Session = Depends(get_db)):
    return payment_service.list_payments(db)

@router.get("/{payment_id}", response_model=PaymentRead, dependencies=[Depends(require_role("staff", "super_admin"))])
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    return payment_service.get_payment(db, payment_id)

@router.post(
    "/",
    response_model=PaymentRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("staff", "super_admin"))],
)
def create_payment(data: PaymentCreate, db: Session = Depends(get_db)):
    return payment_service.create_payment(db, data)

@router.put(
    "/{payment_id}",
    response_model=PaymentRead,
    dependencies=[Depends(require_role("staff", "super_admin"))],
)
def update_payment(payment_id: int, data: PaymentUpdate, db: Session = Depends(get_db)):
    return payment_service.update_payment(db, payment_id, data)

@router.delete(
    "/{payment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("staff", "super_admin"))],
)
def delete_payment(payment_id: int, db: Session = Depends(get_db)):
    return payment_service.delete_payment(db, payment_id)