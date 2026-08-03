from sqlalchemy.orm import Session
from schemas.customers import CustomerCreate, CustomerUpdate
from repositories.customers import customer_repository
from fastapi import HTTPException, status



def get_customer(db:Session, id:int): 
    customer=customer_repository.get(db, id)
    if   not customer:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND, detail=f"Customer with id {id} not found"
        )
    return customer

 
def list_customers(db:Session):
    return customer_repository.get_all(db)

def create_customer(db:Session, data:CustomerCreate): 
     return customer_repository.create(db, data.model_dump())


def update_customer(db:Session, customer_id:int, data:CustomerUpdate): 
    customer=get_customer(db, customer_id)
    return customer_repository.update(db, customer, data.model_dump(exclude_unset=True))

def delete_customer(db:Session, category_id:int): 
    customer=get_customer(db, category_id)
    return customer_repository.delete(db, customer)