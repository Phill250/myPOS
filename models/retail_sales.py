from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class RetailSale(Base):
    __tablename__ = "retail_sales"
    
    sale_id = Column(Integer, primary_key=True, index=True)
    sale_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    total_amount = Column(Integer, nullable=False)  # INT for RWF currency as per documentation
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=True)  # Optional for walk-ins
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)  # Required staff link

    customer = relationship("Customer", back_populates="sales")
    user = relationship("User", back_populates="sales")
    
    items = relationship("RetailSaleItem", back_populates="sale", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="sale", cascade="all, delete-orphan")
    receipts = relationship("Receipt", back_populates="sale", cascade="all, delete-orphan")
