from sqlalchemy.orm import Session
from models.suppliers import Supplier

class SupplierRepository:
    def get(self, db: Session, id: int):
        return db.query(Supplier).filter(Supplier.supplier_id == id).first()

    def get_all(self, db: Session):
        return db.query(Supplier).all()

    def create(self, db: Session, data: dict):
        db_supplier = Supplier(**data)
        db.add(db_supplier)
        db.commit()
        db.refresh(db_supplier)
        return db_supplier

    def update(self, db: Session, db_obj: Supplier, data: dict):
        for key, value in data.items():
            setattr(db_obj, key, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: Supplier):
        db.delete(db_obj)
        db.commit()
        return True

supplier_repository = SupplierRepository()
