from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

class BookBase(BaseModel):
    title: str
    author: str
    isbn: str | None = None
    sale_price: Decimal
    category_id: int
    supplier_id: int 
    retail_stock: int = 0
    library_stock: int = 0

class BookCreate(BookBase):
    pass

class BookUpdate(BookBase):
    title: str | None = None
    author: str | None = None
    isbn: str | None = None
    sale_price: Decimal | None = None
    category_id: int | None = None
    supplier_id: int | None = None 
    retail_stock: int | None = None
    library_stock: int | None = None
        
class BookRead(BookBase):
    model_config = ConfigDict(from_attributes=True)
    
    book_id:int

    