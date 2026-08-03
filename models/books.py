from sqlalchemy import(
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Numeric,
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base

class Book(Base):
    __tablename__ = "books"
    
    book_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    isbn = Column(String, nullable=True)
    sale_price = Column(Numeric(10, 2), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.supplier_id"), nullable=False)
    retail_stock = Column(Integer, nullable=False, default=0)
    library_stock = Column(Integer, nullable=False, default=0)

    
    sale_items = relationship("RetailSaleItem", back_populates="book")
    rental_items = relationship("LibraryRentalItem", back_populates="book")
    category = relationship("Category", back_populates="books")
    supplier = relationship("Supplier", back_populates="books")