from sqlalchemy.orm import Session
from models.books import Book

class BookRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def get(self, db: Session, id:int):
        return db.get (Book, id)
    
    def get_all(self, db: Session):
        return db.query(Book).all()
    
    def get_by_category(self, db: Session, category_id: int):
        books= db.query(Book).filter(Book.category_id == category_id).all()
        return books
    
    def create(self, db: Session, data: dict): 
        book = Book(**data) 
        db.add(book)
        db.commit()
        db.refresh(book)
        return book
    
    def update(self, db: Session, db_obj: Book, data: dict): 
        for field, value in data.items():
            setattr(db_obj, field, value) 
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db:Session, db_obj: Book): 
        db.delete(db_obj)
        db.commit()

    
book_repository = BookRepository(db=None)
    
    
    
        
    
    
        
        