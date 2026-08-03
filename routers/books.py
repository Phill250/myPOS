from fastapi import APIRouter, Depends, status
from database import get_db
from sqlalchemy.orm import Session
from schemas.books import BookCreate, BookRead,  BookUpdate
from services import books as book_service


router= APIRouter( prefix="/books", tags=["books"])

@router.get("/", response_model=list[BookRead])
def  listbooks(db:Session = Depends(get_db)): # used to retrieve all products from the database using the ProductService instance
    return book_service.list_books(db)
            
@router.get("/{book_id}", response_model=BookRead)
def get_book(book_id:int, db:Session = Depends(get_db)): # used to retrieve a single product by its ID from the database using the ProductService instance
    return book_service.get_book(db, book_id)

@router.post("/", response_model=BookRead, status_code=status.HTTP_201_CREATED)
def create_book(data:BookCreate, db:Session = Depends(get_db)): # used to create a new product in the database using the ProductService instance
    return book_service.create_book(db, data)

@router.put("/{book_id}", response_model=BookRead)
def update_book(
    book_id:int, data:BookUpdate, db:Session = Depends(get_db)): # used to update an existing product in the database using the ProductService instance
    return book_service.update_book(db, book_id, data)

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id:int, db:Session = Depends(get_db)): # used to delete a product from the database using the ProductService instance
    return book_service.delete_book(db, book_id)