from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class LibraryRentalItem(Base):
    __tablename__ = "library_rental_items"
    
    rental_item_id = Column(Integer, primary_key=True, index=True)
    rental_id = Column(Integer, ForeignKey("library_rentals.rental_id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.book_id"), nullable=False)

    rental = relationship("LibraryRental", back_populates="items")
    book = relationship("Book", back_populates="rental_items")
