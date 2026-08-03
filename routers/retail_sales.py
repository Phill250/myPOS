from fastapi import APIRouter, Depends, status
from database import get_db
from sqlalchemy.orm import Session
from schemas.retail_sales import RetailSaleCreate, RetailSaleRead, RetailSaleUpdate
from services import retail_sales as retail_sale_service

router = APIRouter(prefix="/sales", tags=["sales"])

@router.get("/", response_model=list[RetailSaleRead])
def list_sales(db: Session = Depends(get_db)):
    return retail_sale_service.list_sales(db)

@router.get("/{sale_id}", response_model=RetailSaleRead)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    return retail_sale_service.get_sale(db, sale_id)

@router.post("/", response_model=RetailSaleRead, status_code=status.HTTP_201_CREATED)
def create_sale(data: RetailSaleCreate, db: Session = Depends(get_db)):
    return retail_sale_service.create_sale(db, data)

@router.put("/{sale_id}", response_model=RetailSaleRead)
def update_sale(sale_id: int, data: RetailSaleUpdate, db: Session = Depends(get_db)):
    return retail_sale_service.update_sale(db, sale_id, data)

@router.delete("/{sale_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sale(sale_id: int, db: Session = Depends(get_db)):
    return retail_sale_service.delete_sale(db, sale_id)
