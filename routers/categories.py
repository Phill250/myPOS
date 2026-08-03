from fastapi import APIRouter, Depends, status
from database import get_db
from sqlalchemy.orm import Session
from schemas.categories import CategoryCreate, CategoryRead,  CategoryUpdate
from services import categories as category_service


router= APIRouter( prefix="/categories", tags=["categories"])

@router.get("/", response_model=list[CategoryRead])
def  listcategories(db:Session = Depends(get_db)): 
    return category_service.list_categories(db)
            
@router.get("/{category_id}", response_model=CategoryRead)
def get_category(category_id:int, db:Session = Depends(get_db)): # used to retrieve a single product by its ID from the database using the ProductService instance
    return category_service.get_category(db, category_id)

@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(data:CategoryCreate, db:Session = Depends(get_db)): # used to create a new product in the database using the ProductService instance
    return category_service.create_category(db, data)

@router.put("/{category_id}", response_model=CategoryRead)
def update_category(
    category_id:int, data:CategoryUpdate, db:Session = Depends(get_db)): # used to update an existing product in the database using the ProductService instance
    return category_service.update_category(db, category_id, data)

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id:int, db:Session = Depends(get_db)): # used to delete a product from the database using the ProductService instance
    return category_service.delete_category(db, category_id)