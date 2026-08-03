from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Payment(Base):
    __tablename__ = "payments"
    
    payment_id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False)
    transaction_type = Column(String(50), nullable=False)
    sale_id = Column(Integer, ForeignKey("retail_sales.sale_id"), nullable=True)
    rental_id = Column(Integer, ForeignKey("library_rentals.rental_id"), nullable=True)

    sale = relationship("RetailSale", back_populates="payments")
    rental = relationship("LibraryRental", back_populates="payments")
