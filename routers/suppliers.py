from fastapi import APIRouter, Depends, status
from database import get_db
from sqlalchemy.orm import Session
from schemas.suppliers import SupplierCreate, SupplierRead, SupplierUpdate
from services import suppliers as supplier_service
from dependencies import require_role

router = APIRouter(
    prefix="/suppliers",
    tags=["suppliers"],
    dependencies=[Depends(require_role("staff", "super_admin"))],  # not visible to customers at all
)

@router.get("/", response_model=list[SupplierRead])
def list_suppliers(db: Session = Depends(get_db)):
    return supplier_service.list_suppliers(db)

@router.get("/{supplier_id}", response_model=SupplierRead)
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    return supplier_service.get_supplier(db, supplier_id)

@router.post("/", response_model=SupplierRead, status_code=status.HTTP_201_CREATED)
def create_supplier(data: SupplierCreate, db: Session = Depends(get_db)):
    return supplier_service.create_supplier(db, data)

@router.put("/{supplier_id}", response_model=SupplierRead)
def update_supplier(supplier_id: int, data: SupplierUpdate, db: Session = Depends(get_db)):
    return supplier_service.update_supplier(db, supplier_id, data)

@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    return supplier_service.delete_supplier(db, supplier_id)