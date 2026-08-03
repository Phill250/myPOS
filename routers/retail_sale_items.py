from fastapi import APIRouter, Depends, status
from database import get_db
from sqlalchemy.orm import Session
from schemas.retail_sale_items import RetailSaleItemCreate, RetailSaleItemRead, RetailSaleItemUpdate
from services import retail_sale_items as sale_item_service

router = APIRouter(prefix="/sale-items", tags=["sale-items"])

@router.get("/", response_model=list[RetailSaleItemRead])
def list_sale_items(db: Session = Depends(get_db)):
    return sale_item_service.list_sale_items(db)

@router.get("/{sale_item_id}", response_model=RetailSaleItemRead)
def get_sale_item(sale_item_id: int, db: Session = Depends(get_db)):
    return sale_item_service.get_sale_item(db, sale_item_id)

@router.post("/", response_model=RetailSaleItemRead, status_code=status.HTTP_201_CREATED)
def create_sale_item(data: RetailSaleItemCreate, db: Session = Depends(get_db)):
    return sale_item_service.create_sale_item(db, data)

@router.put("/{sale_item_id}", response_model=RetailSaleItemRead)
def update_sale_item(sale_item_id: int, data: RetailSaleItemUpdate, db: Session = Depends(get_db)):
    return sale_item_service.update_sale_item(db, sale_item_id, data)

@router.delete("/{sale_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sale_item(sale_item_id: int, db: Session = Depends(get_db)):
    return sale_item_service.delete_sale_item(db, sale_item_id)
