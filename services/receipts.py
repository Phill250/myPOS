from sqlalchemy.orm import Session
from schemas.receipts import ReceiptCreate, ReceiptUpdate
from repositories.receipts import receipt_repository
from fastapi import HTTPException, status

def get_receipt(db: Session, id: int): 
    receipt = receipt_repository.get(db, id)
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Receipt record with id {id} not found"
        )
    return receipt

def list_receipts(db: Session):
    return receipt_repository.get_all(db)

def create_receipt(db: Session, data: ReceiptCreate): 
    # Business logic validation: Ensure either a sale_id or a rental_id is linked
    if not data.sale_id and not data.rental_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A receipt must be linked to either a sale_id or a rental_id"
        )
    return receipt_repository.create(db, data.model_dump())

def update_receipt(db: Session, receipt_id: int, data: ReceiptUpdate): 
    receipt = get_receipt(db, receipt_id)
    return receipt_repository.update(db, receipt, data.model_dump(exclude_unset=True))

def delete_receipt(db: Session, receipt_id: int): 
    receipt = get_receipt(db, receipt_id)
    return receipt_repository.delete(db, receipt)
