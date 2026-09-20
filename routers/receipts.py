from fastapi import APIRouter, Depends, HTTPException, status
from database import get_db
from sqlalchemy.orm import Session
from schemas.receipts import ReceiptCreate, ReceiptRead, ReceiptUpdate
from services import receipts as receipt_service
from dependencies import get_current_user, require_role

router = APIRouter(
    prefix="/receipts",
    tags=["receipts"],
    dependencies=[Depends(get_current_user)],
)


def _receipt_customer_id(receipt) -> int | None:
    """A receipt belongs to whichever transaction it's linked to."""
    if receipt.sale is not None:
        return receipt.sale.customer_id
    if receipt.rental is not None:
        return receipt.rental.customer_id
    return None


@router.get("/", response_model=list[ReceiptRead])
def list_receipts(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role == "customer":
        linked = getattr(current_user, "customer_profile", None)
        if not linked:
            return []
        all_receipts = receipt_service.list_receipts(db)
        return [r for r in all_receipts if _receipt_customer_id(r) == linked.customer_id]
    return receipt_service.list_receipts(db)


@router.get("/{receipt_id}", response_model=ReceiptRead)
def get_receipt(receipt_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    receipt = receipt_service.get_receipt(db, receipt_id)

    if current_user.role == "customer":
        linked = getattr(current_user, "customer_profile", None)
        if not linked or _receipt_customer_id(receipt) != linked.customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not your receipt",
            )

    return receipt


@router.post(
    "/",
    response_model=ReceiptRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("staff", "super_admin"))],
)
def create_receipt(data: ReceiptCreate, db: Session = Depends(get_db)):
    return receipt_service.create_receipt(db, data)


@router.put(
    "/{receipt_id}",
    response_model=ReceiptRead,
    dependencies=[Depends(require_role("staff", "super_admin"))],
)
def update_receipt(receipt_id: int, data: ReceiptUpdate, db: Session = Depends(get_db)):
    return receipt_service.update_receipt(db, receipt_id, data)


@router.delete(
    "/{receipt_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("staff", "super_admin"))],
)
def delete_receipt(receipt_id: int, db: Session = Depends(get_db)):
    return receipt_service.delete_receipt(db, receipt_id)