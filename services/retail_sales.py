from sqlalchemy.orm import Session
from schemas.retail_sales import RetailSaleCreate, RetailSaleUpdate
from repositories.retail_sales import retail_sale_repository
from fastapi import HTTPException, status

def get_sale(db: Session, id: int): 
    sale = retail_sale_repository.get(db, id)
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Retail sale record with id {id} not found"
        )
    return sale

def list_sales(db: Session):
    return retail_sale_repository.get_all(db)

def list_sales_for_customer(db: Session, customer_id: int):
    return retail_sale_repository.get_all_for_customer(db, customer_id)

def create_sale(db: Session, data: RetailSaleCreate): 
    from models.users import User
    user_exists = db.query(User).filter(User.user_id == data.user_id).first()
    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Staff member with user_id {data.user_id} does not exist."
        )
    return retail_sale_repository.create(db, data.model_dump())

def update_sale(db: Session, sale_id: int, data: RetailSaleUpdate): 
    sale = get_sale(db, sale_id)
    return retail_sale_repository.update(db, sale, data.model_dump(exclude_unset=True))

def delete_sale(db: Session, sale_id: int): 
    sale = get_sale(db, sale_id)
    return retail_sale_repository.delete(db, sale)