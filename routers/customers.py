from fastapi import APIRouter, Depends, status
from database import get_db
from sqlalchemy.orm import Session
from schemas.customers import CustomerCreate, CustomerRead,  CustomerUpdate
from services import customers as customer_service


router= APIRouter( prefix="/customers", tags=["customers"])

@router.get("/", response_model=list[CustomerRead])
def  listcategories(db:Session = Depends(get_db)): 
    return customer_service.list_customer(db)
            
@router.get("/{customer_id}", response_model=CustomerRead)
def get_customer(customer_id:int, db:Session = Depends(get_db)): # used to retrieve a single product by its ID from the database using the ProductService instance
    return customer_service.get_customer(db, customer_id)

@router.post("/", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
def create_customer(data:CustomerCreate, db:Session = Depends(get_db)): # used to create a new product in the database using the ProductService instance
    return customer_service.create_customer(db, data)

@router.put("/{customer_id}", response_model=CustomerRead)
def update_customer(
    customer_id:int, data:CustomerUpdate, db:Session = Depends(get_db)): # used to update an existing product in the database using the ProductService instance
    return customer_service.update_category(db, customer_id, data)

@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(customer_id:int, db:Session = Depends(get_db)): # used to delete a product from the database using the ProductService instance
    return customer_service.delete_customer(db, customer_id)