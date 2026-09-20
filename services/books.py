from sqlalchemy.orm import Session
from schemas.books import BookCreate, BookUpdate
from repositories.books import book_repository
from fastapi import HTTPException, status



def get_book(db:Session, book_id:int): 
    book=book_repository.get(db, book_id)
    if   not book:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND, detail=f"Product with id {book_id} not found"
        )
    return book

 
def list_books(db:Session):
    return book_repository.get_all(db)

def create_book(db:Session, data:BookCreate): 
     return book_repository.create(db, data.model_dump())


def update_book(db:Session, book_id:int, data:BookUpdate): 
    book=get_book(db, book_id)
    return book_repository.update(db, book, data.model_dump(exclude_unset=True))

def delete_book(db:Session, book_id:int): 
    book=get_book(db, book_id)
    return book_repository.delete(db, book)