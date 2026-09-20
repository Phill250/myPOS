from sqlalchemy import(
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Numeric,
)

from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func

from database import Base

class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True, unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    email = Column(String, nullable=False)
    library_member = Column(Boolean, nullable=False)

    user = relationship("User", backref=backref("customer_profile", uselist=False))
    sales = relationship("RetailSale", back_populates="customer")
    rentals = relationship("LibraryRental", back_populates="customer")