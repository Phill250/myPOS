from fastapi import APIRouter, Depends, HTTPException, status
from database import get_db
from sqlalchemy.orm import Session
from schemas.retail_sales import RetailSaleCreate, RetailSaleRead, RetailSaleUpdate
from services import retail_sales as retail_sale_service
from dependencies import get_current_user, require_role

router = APIRouter(
    prefix="/sales",
    tags=["sales"],
    dependencies=[Depends(get_current_user)],  # baseline: must be logged in for every route below
)


@router.get("/", response_model=list[RetailSaleRead])
def list_sales(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role == "customer":
        linked = getattr(current_user, "customer_profile", None)
        if not linked:
            return []  # a customer with no linked profile has no sales to show
        return retail_sale_service.list_sales_for_customer(db, linked.customer_id)
    return retail_sale_service.list_sales(db)


@router.get("/{sale_id}", response_model=RetailSaleRead)
def get_sale(sale_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    sale = retail_sale_service.get_sale(db, sale_id)

    if current_user.role == "customer":
        linked = getattr(current_user, "customer_profile", None)
        if not linked or sale.customer_id != linked.customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not your sale",
            )

    return sale


@router.post(
    "/",
    response_model=RetailSaleRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("staff", "super_admin"))],
)
def create_sale(data: RetailSaleCreate, db: Session = Depends(get_db)):
    return retail_sale_service.create_sale(db, data)


@router.put(
    "/{sale_id}",
    response_model=RetailSaleRead,
    dependencies=[Depends(require_role("staff", "super_admin"))],
)
def update_sale(sale_id: int, data: RetailSaleUpdate, db: Session = Depends(get_db)):
    return retail_sale_service.update_sale(db, sale_id, data)


@router.delete(
    "/{sale_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("staff", "super_admin"))],
)
def delete_sale(sale_id: int, db: Session = Depends(get_db)):
    return retail_sale_service.delete_sale(db, sale_id)