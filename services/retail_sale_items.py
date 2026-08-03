from sqlalchemy.orm import Session
from schemas.retail_sale_items import RetailSaleItemCreate, RetailSaleItemUpdate
from repositories.retail_sale_items import sale_item_repository
from repositories.books import book_repository  # Imports the book repository to modify stock slots
from fastapi import HTTPException, status

def get_sale_item(db: Session, id: int): 
    item = sale_item_repository.get(db, id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Sale item with id {id} not found"
        )
    return item

def list_sale_items(db: Session):
    return sale_item_repository.get_all(db)

def create_sale_item(db: Session, data: RetailSaleItemCreate): 
    book = book_repository.get(db, data.book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {data.book_id} does not exist"
        )
        
    if book.retail_stock < data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient retail stock. Only {book.retail_stock} copies left."
        )
        
    book.retail_stock -= data.quantity
    db.commit()     
    return sale_item_repository.create(db, data.model_dump())

def update_sale_item(db: Session, sale_item_id: int, data: RetailSaleItemUpdate): 
    item = get_sale_item(db, sale_item_id)
    return sale_item_repository.update(db, item, data.model_dump(exclude_unset=True))

def delete_sale_item(db: Session, sale_item_id: int): 
    item = get_sale_item(db, sale_item_id)
    return sale_item_repository.delete(db, item)
