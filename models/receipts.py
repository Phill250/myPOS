from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Receipt(Base):
    __tablename__ = "receipts"
    
    receipt_id = Column(Integer, primary_key=True, index=True)
    receipt_number = Column(String(50), nullable=False)
    printed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    sale_id = Column(Integer, ForeignKey("retail_sales.sale_id"), nullable=True)
    rental_id = Column(Integer, ForeignKey("library_rentals.rental_id"), nullable=True)

    sale = relationship("RetailSale", back_populates="receipts")
    rental = relationship("LibraryRental", back_populates="receipts")
