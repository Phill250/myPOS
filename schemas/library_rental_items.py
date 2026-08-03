from pydantic import BaseModel, ConfigDict

class LibraryRentalItemBase(BaseModel):
    rental_id: int
    book_id: int

class LibraryRentalItemCreate(LibraryRentalItemBase):
    pass

class LibraryRentalItemUpdate(BaseModel):
    rental_id: int | None = None
    book_id: int | None = None

class LibraryRentalItemRead(LibraryRentalItemBase):
    model_config = ConfigDict(from_attributes=True)
    
    rental_item_id: int
