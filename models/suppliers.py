from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class Supplier(Base):
    __tablename__ = "suppliers"
    
    supplier_id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=False)

    books = relationship("Book", back_populates="supplier")
