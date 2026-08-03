from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class RetailSaleItem(Base):
    __tablename__ = "retail_sale_items"
    
    sale_item_id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("retail_sales.sale_id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.book_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_snapshot = Column(Float, nullable=False)
   
       
    sale = relationship("RetailSale", back_populates="items")
    book = relationship("Book", back_populates="sale_items")
