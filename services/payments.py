from sqlalchemy.orm import Session
from schemas.payments import PaymentCreate, PaymentUpdate
from repositories.payments import payment_repository
from fastapi import HTTPException, status

def get_payment(db: Session, id: int): 
    payment = payment_repository.get(db, id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Payment record with id {id} not found"
        )
    return payment

def list_payments(db: Session):
    return payment_repository.get_all(db)

def create_payment(db: Session, data: PaymentCreate): 
    # Business logic validation: Ensure either a sale_id or a rental_id is linked
    if not data.sale_id and not data.rental_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A payment must be linked to either a sale_id or a rental_id"
        )
    return payment_repository.create(db, data.model_dump())

def update_payment(db: Session, payment_id: int, data: PaymentUpdate): 
    payment = get_payment(db, payment_id)
    return payment_repository.update(db, payment, data.model_dump(exclude_unset=True))

def delete_payment(db: Session, payment_id: int): 
    payment = get_payment(db, payment_id)
    return payment_repository.delete(db, payment)
