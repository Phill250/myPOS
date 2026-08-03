from sqlalchemy import Column, Integer, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class LibraryRental(Base):
    __tablename__ = "library_rentals"
    
    rental_id = Column(Integer, primary_key=True, index=True)
    rental_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expected_return = Column(Date, nullable=False)
    actual_return = Column(Date, nullable=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    customer = relationship("Customer", back_populates="rentals")
    user = relationship("User", back_populates="rentals")
    payments = relationship("Payment", back_populates="rental")
    items = relationship("LibraryRentalItem", back_populates="rental", cascade="all, delete-orphan")
    receipts = relationship("Receipt", back_populates="rental")